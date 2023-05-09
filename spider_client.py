import getopt
import sys
import time
import spider_category

def main(argv):
    category, keyword, start_time, end_time = __get_arg(argv)
    spider_category.PROGRESS_BAR_DISABLE = False
    spider_category.SPIDER_CATEGORY[category].spider_with_client(keyword=keyword, start_time=start_time, end_time=end_time)

# 命令行交互
def __get_arg(argv):
    help_usage = '''
        NOTE: 欢迎使用gxcg网爬取工具。本工具仅做学习交流使用，爬取的所有公告数据均已在网站公开。请耐心等待执行结果，程序会定时暂停，模拟人的浏览操作行为，避免爬取过快被服务端识别

        USAGE: python spider_client.py [OPTIONS]

        OPTIONS: 
          -h,--help      use the help manual
          -c,--category  article type.0-中标成交结果公告
          -k,--keyword   query keyword
          -s,--start     query start time
          -e,--end       query end time
          -p,--proxy     local ip proxy

        EXAMPLES: 
          python spider_client.py -h
          python spider_client.py help

          python spider_client.py
          python spider_client.py -c 0 -k 社会福利院 -s 2021-12-01 -e 2023-04-20
          python spider_client.py --category 0 --keyword 社会福利院 --start 2021-12-01 --end 2023-04-20
        '''

    category = ''
    keyword = ''
    start_time = ''
    end_time = ''

    # 定义短选项和长选项
    short_opts = 'hc:k:s:e:'
    long_opts = ['help', 'category=', 'keyword=', 'start=', 'end=']
    # 解析命令行参数
    try:
        options, args = getopt.getopt(argv, short_opts, long_opts)
    except:
        print(help_usage)
        # 异常退出
        sys.exit(2)
    for name, value in options:
        if name in ('-h', '--help'):
            print(help_usage)
            # 正常退出
            sys.exit()
        if name in ('-c', '--category'):
            if value in spider_category.SPIDER_CATEGORY.keys():
                category = value
            else:
                print(help_usage)
                sys.exit()
        if name in ('-k', '--keyword'):
            keyword = value
            continue
        if name in ('-s', '--start'):
            start_time = value
            continue
        if name in ('-e', '--end'):
            end_time = value
            continue
        if name in ('-p', '--proxy') and value != '':
            spider_category.SPIDER_CATEGORY[category].PROXIES = {value}
            continue

    if category == '':
        print(help_usage)
        sys.exit()
    # 避免一次查询过量数据
    if start_time == '' and end_time == '':
        start_time = time.strftime('%Y-%m-%d', time.localtime())
        end_time = start_time
    print('输入参数: 类别={0}, 关键字={1}, 起始时间={2}, 结束时间={3}'.format(spider_category.SPIDER_CATEGORY[category].CATEGORY_NAME, keyword, start_time, end_time))
    return category, keyword, start_time, end_time

if __name__ == "__main__":
    # arg = ['-c0', '-k社会福利院', '-s2021-12-01', '-e2023-04-20']
    arg = sys.argv[1:]
    main(arg)