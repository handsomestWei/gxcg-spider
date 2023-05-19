import os
import traceback
import flask
from flask import request, render_template, jsonify
from cron_lite import cron_task, start_all
import time
import spider_category

server = flask.Flask(__name__)

@server.route("/")
@server.route("/index.html")
def index():
    return render_template('index.html')

# TODO 增加下载记录日志
@server.route('/gxcg-spider/excel', methods=['get'])
def download_excel_result():
    category = request.values.get('category')
    keyword = request.values.get('keyword')
    start_time = request.values.get('startTime')
    end_time = request.values.get('endTime')
    file_path = spider_category.SPIDER_CATEGORY[category]\
        .export_excel_from_db(keyword=keyword, start_time=start_time, end_time=end_time)
    response = flask.send_file(file_path)
    return response

@server.route('/gxcg-spider/data', methods=['get'])
def query_data():
    category = request.values.get('category')
    keyword = request.values.get('keyword')
    start_time = request.values.get('startTime')
    end_time = request.values.get('endTime')
    data = spider_category.SPIDER_CATEGORY[category]\
        .query_data(keyword=keyword, start_time=start_time, end_time=end_time)

    rsp = {}
    rsp['code'] = '200'
    rsp['msg'] = 'success'
    rsp['data'] = data
    return jsonify(rsp)

@server.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@server.errorhandler(Exception)
def internal_server_error(e):
    traceback.print_exc()
    return render_template('500.html'), 500

# 每天定时爬取当日数据
@cron_task("0 0/12 * * *")
def spider_task():
    print("spider task start", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())))
    start_time = time.strftime("%Y-%m-%d", time.localtime(time.time()))
    for value in spider_category.SPIDER_CATEGORY.values():
        value.spider_with_server(keyword='', start_time=start_time, end_time=start_time)
    print("spider task end", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())))

# 文件下载后删除定时清理
@cron_task("*/5 * * * *")
def clean_output_task():
    print("clean output task start", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())))
    file_list = __get_dir_file_info(spider_category.EXCEL_OUT_PUT_DIR)
    for file_info in file_list:
        try:
            os.remove(file_info[0])
        except:
            traceback.print_exc()
    print("clean output task end", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())))

def __get_dir_file_info(dir):
    file_list = []
    for f in os.listdir(dir):
        path = os.path.join(dir, f)
        stat = os.stat(path)
        file_list.append([path, time.ctime(stat.st_ctime)])
    return file_list

if __name__ == '__main__':
    spider_category.PROGRESS_BAR_DISABLE = True
    for value in spider_category.SPIDER_CATEGORY.values():
        value.init_db_data()
    start_all(spawn=True)
    server.run(debug=True, port=8765, host='0.0.0.0')