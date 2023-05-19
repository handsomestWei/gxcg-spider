# -*- coding: utf-8 -*-

import _thread
import ast
import json
import sqlite3
import time
import traceback
import urllib
import numpy as np
import openpyxl
import requests
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm
import spider_category

# 配置和使用代理池，避免被封ip
PROXIES = {}
# 编码：中标成交结果公告
CATEGORY_CODE_RESULT_WIN_BID = 'ZcyAnnouncement3004'
CATEGORY_NAME = '中标成交结果公告'

# 公告详情对象
class CategoryDetail():
    # 分类
    category = ''
    # 文章标题
    title = ""
    # 项目编号
    project_code = ""
    # 项目名称
    project_name = ""
    # 文章发布日期
    publish_date = ""
    # 文章链接
    url = ""
    # 中标价格
    win_bid_price = ""
    # 中标供应商名称
    win_bid_supply_name = ""
    # 中标供应商地址
    win_bid_supply_addr = ""
    # 文章内容
    content = ""

    def __init__(self, category='', title='', project_code='', project_name='', publish_date='',
                 url='', win_bid_price='', win_bid_supply_name='', win_bid_supply_addr='', content=''):
        self.category = category
        self.title = title
        self.project_code = project_code
        self.project_name = project_name
        self.publish_date = publish_date
        self.url = url
        self.win_bid_price = win_bid_price
        self.win_bid_supply_name = win_bid_supply_name
        self.win_bid_supply_addr = win_bid_supply_addr
        self.content = content

# 爬取中标成交结果公告
def spider(keyword='', start_time='', end_time=''):
    # step1：抓取网页数据
    category_details = __spider_web_page(keyword=keyword, start_time=start_time, end_time=end_time)
    # step2：解析网页数据
    category_details = __analyze_web_page(category_details)
    return category_details, keyword, start_time, end_time

# 爬取中标成交结果公告。客户端用，结果导出到excel
def spider_with_client(keyword='', start_time='', end_time=''):
    category_details, keyword, start_time, end_time = spider(keyword=keyword, start_time=start_time, end_time=end_time)
    # step3：数据导出到excel文件
    file_name = __set_excel_file_name(keyword, start_time, end_time)
    file_path = spider_category.EXCEL_OUT_PUT_DIR + file_name
    __export_excel(category_details, file_path)

# 爬取中标成交结果公告。服务端用，结果存入数据库
def spider_with_server(keyword='', start_time='', end_time=''):
    category_details, keyword, start_time, end_time = spider(keyword=keyword, start_time=start_time, end_time=end_time)
    # step3：数据写入数据库
    __save_db(keyword, category_details)

# 导出数据到excel
def export_excel_from_db(keyword='', start_time='', end_time=''):
    category_details = __select_db(keyword, start_time, end_time)
    file_name = __set_excel_file_name(keyword, start_time, end_time)
    file_path = spider_category.EXCEL_OUT_PUT_DIR + file_name
    __export_excel(category_details, file_path)
    return file_path

# 数据查询
def query_data(keyword='', start_time='', end_time=''):
    data = []
    category_details = __select_db(keyword, start_time, end_time)
    for detail in category_details:
        # 对象转json，并去掉转义符
        json_str = json.dumps(detail.__dict__, ensure_ascii=False)
        json_str = ast.literal_eval(json_str)
        data.append(json_str)
    return data

# 初始化数据
def init_db_data():
    conn = None
    try:
        conn = sqlite3.connect(spider_category.DB_PATH)
        conn.execute('''CREATE TABLE IF NOT EXISTS category_result_win_bid
                             (project_code TEXT PRIMARY KEY NOT NULL,
                             category TEXT, project_name TEXT, title TEXT, publish_date date,
                             win_bid_price TEXT, win_bid_supply_name TEXT, win_bid_supply_addr TEXT,
                             url TEXT, content TEXT);''')
        rows = conn.execute("SELECT count(*) from category_result_win_bid").fetchall()
        row = rows[0]
        if row[0] == 0:
            # 异步执行，避免阻塞主线程
            _thread.start_new_thread(spider_with_server, ('', time.strftime("%Y-01-01", time.localtime()), ''))
    except:
        traceback.print_exc()
        return False
    finally:
        if conn != None:
            try:
                conn.close()
            except:
                traceback.print_exc()

def __select_db(keyword='', start_time='', end_time=''):
    category_details = []
    conn = None
    try:
        conn = sqlite3.connect(spider_category.DB_PATH)
        query_sql = ' 1 == 1'
        if keyword != '':
            query_sql += " and title like '%" + keyword + "%'"
        if start_time != '':
            query_sql += ' and date(publish_date) >= ' + "'" + start_time + "'"
        if end_time != '':
            query_sql += ' and date(publish_date) <= ' "'" + end_time + "'"
        rows = conn.execute("SELECT * from category_result_win_bid where" + query_sql + " order by publish_date desc").fetchall()
        for row in rows:
            category_detail = CategoryDetail()
            category_details.append(category_detail)
            category_detail.project_code = row[0]
            category_detail.category = row[1]
            category_detail.project_name = row[2]
            category_detail.title = row[3]
            category_detail.publish_date = row[4]
            category_detail.win_bid_price = row[5]
            category_detail.win_bid_supply_name = row[6]
            category_detail.win_bid_supply_addr = row[7]
            category_detail.url = row[8]
            # category_detail.content = row[9]
        return category_details
    except:
        traceback.print_exc()
        return category_details
    finally:
        if conn != None:
            try:
                conn.close()
            except:
                traceback.print_exc()

# 抓取网页数据
def __spider_web_page(keyword='', start_time='', end_time=''):
    category_details = []
    try:
        article_id_url_d = __page_query_category(keyword=keyword, start_time=start_time, end_time=end_time)
        # 进度条打印到控制台
        for article_id, url in tqdm(article_id_url_d.items(), desc='【第一步】爬取网页', colour='GREEN', disable=spider_category.PROGRESS_BAR_DISABLE):
            # 暂停，模拟人的浏览操作行为，避免爬取过快被服务端识别
            time.sleep(1)
            data = __query_category_detail(url)
            category_detail = CategoryDetail()
            category_details.append(category_detail)
            category_detail.title = data.get("title")
            category_detail.project_code = data.get("projectCode")
            category_detail.project_name = data.get("projectName")
            category_detail.content = data.get("content")
            if data.get("publishDate") != None and len(str(data.get("publishDate"))) == 13:
                # 13位毫秒时间戳转年月日
                category_detail.publish_date = time.strftime("%Y-%m-%d", time.localtime(float(data.get("publishDate") / 1000)))
            # 根据文章id获取对应页面链接
            if data.get("announcementLinkDtoList") != None and len(data.get("announcementLinkDtoList")) > 0:
                for link_dto in data.get("announcementLinkDtoList"):
                    if article_id == link_dto.get("articleId"):
                        category_detail.url = link_dto.get("url")
                        category_detail.publish_date = link_dto.get("publishDate")
                        break
    except:
        traceback.print_exc()
    return category_details

# 解析和清洗网页数据
def __analyze_web_page(category_details=[]):
    # 进度条打印到控制台
    for category_detail in tqdm(category_details, desc='【第二步】解析网页', colour='GREEN', disable=spider_category.PROGRESS_BAR_DISABLE):
        try:
            # 使用bs4库的html解析器
            # print(BeautifulSoup(category_detail.content, "html.parser").prettify())
            soup = BeautifulSoup(category_detail.content, "html.parser")
            # 策略一：抽取文章表格内带有特定样式的内容
            rs, category_detail = __analyze_article_table(soup, category_detail)
            if rs:
                continue
            # 策略二：抽取文章第一个表格内容，按关键字搜索
            rs, category_detail = __analyze_article_table_content(soup, category_detail)
            if rs:
                continue
            # 策略三：抽取文章所有行，按关键字搜索
            rs, category_detail = __analyze_article_p(soup, category_detail)
            if rs:
                continue
        except:
            traceback.print_exc()
    return category_details

# 导出excel
def __export_excel(category_details=[], file_path=''):
    data = []
    # 进度条打印到控制台
    for i in tqdm(range(len(category_details)), desc='【第三步】导出excel', colour='GREEN', disable=spider_category.PROGRESS_BAR_DISABLE):
        category_detail = category_details[i]
        dic = {}
        dic['序号'] = str(i + 1)
        dic['标题'] = category_detail.title
        dic['发布时间'] = category_detail.publish_date
        dic['项目编号'] = category_detail.project_code
        dic['项目名称'] = category_detail.project_name
        dic['中标成交价格'] = category_detail.win_bid_price
        dic['供应商名称'] = category_detail.win_bid_supply_name
        dic['供应商地址'] = category_detail.win_bid_supply_addr
        dic['公告地址'] = category_detail.url
        data.append(dic)
    __export_excel_auto_column_weight(file_path, data)

# 存数据库
def __save_db(keyword, category_details=[]):
    conn = None
    try:
        conn = sqlite3.connect(spider_category.DB_PATH)
        for category_detail in category_details:
            if category_detail.project_code == '':
                continue
            data = []
            data.append(category_detail.project_code)
            # TODO data.append(keyword)
            data.append('')
            data.append(category_detail.project_name)
            data.append(category_detail.title)
            data.append(category_detail.publish_date)
            data.append(category_detail.win_bid_price)
            data.append(category_detail.win_bid_supply_name)
            data.append(category_detail.win_bid_supply_addr)
            data.append(category_detail.url)
            data.append(category_detail.content)
            conn.execute('insert or ignore into category_result_win_bid VALUES (?,?,?,?,?,?,?,?,?,?)', data)
            conn.commit()
        return True
    except:
        traceback.print_exc()
        return False
    finally:
        if conn != None:
            try:
                conn.close()
            except:
                traceback.print_exc()

# 分页查询项目
def __page_query_category(keyword='', start_time='', end_time=''):
    # key=文章id，value=文章详情url
    article_id_url_d = {}
    total = __query_category(keyword=keyword, page_no=1, start_time=start_time, end_time=end_time).get('total')
    print('查询结果：' + str(total) + '条')
    page = total // 100
    if total % 100 > 0:
        page = page + 1

    for i in range(1, page + 1):
        # 暂停，模拟人的浏览操作，避免爬取过快被服务端识别
        time.sleep(1)
        datas = __query_category(keyword=keyword, page_no=i, start_time=start_time, end_time=end_time).get('data')
        for data in datas:
            article_id = data.get('articleId')
            # 对参数encode
            url = "http://zfcg.gxzf.gov.cn/portal/detail?articleId=" + urllib.parse.quote(article_id)
            article_id_url_d[article_id] = url
    return article_id_url_d

# 查询项目
def __query_category(keyword='', page_no=1, start_time='', end_time=''):
    category_url = "http://zfcg.gxzf.gov.cn/portal/category"
    reqBody = {"pageNo": page_no, "pageSize": 100, "publishDateBegin": start_time, "publishDateEnd": end_time,
               "categoryCode": CATEGORY_CODE_RESULT_WIN_BID, "keyword": keyword}
    if len(PROXIES) > 0:
        response = requests.post(url=category_url, json=reqBody, headers=spider_category.HEADERS, proxies=PROXIES, verify=False)
    else:
        response = requests.post(url=category_url, json=reqBody, headers=spider_category.HEADERS, verify=False)
    if response.content:
        return response.json().get('result').get('data')

# 查询项目详情
def __query_category_detail(category_url=''):
    if len(PROXIES) > 0:
        response = requests.get(url=category_url, headers=spider_category.HEADERS, proxies=PROXIES, verify=False)
    else:
        response = requests.get(url=category_url, headers=spider_category.HEADERS, verify=False)
    if response.content:
        return response.json().get("result").get("data")

# 抽取文章表格内带有特定样式的内容
def __analyze_article_table(soup, category_detail):
    rs = soup.find_all('td', {'class': 'code-summaryPrice'})
    if len(rs) == 0:
        return False, category_detail
    category_detail.win_bid_price = rs[0].get_text(strip=True)
    category_detail.win_bid_supply_name = soup.find_all('td', {'class': 'code-winningSupplierName'})[0].get_text(strip=True)
    category_detail.win_bid_supply_addr = soup.find_all('td', {'class':'code-winningSupplierAddr'})[0].get_text(strip=True)
    return True, category_detail

# 抽取文章所有行，按关键字搜索
def __analyze_article_p(soup, category_detail):
    rs = False
    ps = soup.find_all('p')
    for p in ps:
        # 判断是否包含关键字，按中文冒号分隔
        text = p.get_text(strip=True)
        if text == "":
            continue
        if "中标" in text and "金额" in text and category_detail.win_bid_price == '':
            category_detail.win_bid_price = text
            rs = True
            continue
        if "供应商名称" in text and category_detail.win_bid_supply_name == '':
            category_detail.win_bid_supply_name = text
            rs = True
            continue
        if "供应商地址" in text and category_detail.win_bid_supply_addr == '':
            category_detail.win_bid_supply_addr = text
            rs = True
            continue
    return rs, category_detail

# 抽取文章第一个表格内容，按关键字搜索
def __analyze_article_table_content(soup, category_detail):
    tbs = soup.find_all('table')
    if len(tbs) == 0:
        return False, category_detail
    # 取第一个表格第三列内容
    # 将换行符<br />替换为特殊标记，获取内容后再按标记分隔。也可以先查找所有br标签后，使用next_siblings()等函数移动查找上下节点。也可以使用正则表达式捕获特定内容
    if len(tbs[0].find_all('td')[5].find_all('br')) < 2:
        return False, category_detail
    for br in tbs[0].find_all('td')[5].find_all('br'):
        br.replace_with(spider_category.HTML_BR_REPLACE_TARGET)
    lines = tbs[0].find_all('td')[5].find_all('p')[0].get_text(strip=True).split(spider_category.HTML_BR_REPLACE_TARGET)
    category_detail.win_bid_supply_name = __split_colon(lines[0])
    category_detail.win_bid_supply_addr = __split_colon(lines[1])
    category_detail.win_bid_price = __split_colon(lines[2])
    return True, category_detail

# 导出excel并自动设置列宽
def __export_excel_auto_column_weight(file_path, data, sheet_name='Sheet1'):
    df = pd.DataFrame(data)
    writer = pd.ExcelWriter(file_path, engine='openpyxl')
    # 需要设置index=False，否则后续列宽计算有误
    df.to_excel(writer, index=False)
    # 数据输出到excel后，自动设置列宽
    try:
        # 计算表头的字符宽度
        column_widths = (
            df.columns.to_series().apply(lambda x: len(x.encode('gbk'))).values
        )
        # 计算每列的最大字符宽度
        max_widths = (
            df.astype(str).applymap(lambda x: len(x.encode('gbk'))).agg(max).values
        )
        # 计算整体最大宽度
        widths = np.max([column_widths, max_widths], axis=0)
        # 设置列宽
        worksheet = writer.sheets[sheet_name]
        for i, width in enumerate(widths, 1):
            # openpyxl引擎设置字符宽度时会缩水0.5左右个字符，所以干脆+2使左右都空出一个字宽。
            worksheet.column_dimensions[openpyxl.utils.get_column_letter(i)].width = width + 2
    except:
        traceback.print_exc()
    # 保存设置
    writer.save()
    print('结果导出完成：' + file_path)

# 冒号分隔，处理比如'投标价格：123元'=>'123元'
def __split_colon(str=''):
    if '：' in str:
        return str.split('：')[1]
    if ':' in str:
        return str.split(':')[1]
    return str

# 生成输出文件名，包含搜索关键字、起始结束时间
def __set_excel_file_name(keyword, start_time, end_time):
    file_name = CATEGORY_NAME
    if keyword != '':
        file_name += '-' + keyword
    file_name += "-时间" + '(' + start_time + '~' + end_time + ')'
    file_name += '.xlsx'
    return file_name