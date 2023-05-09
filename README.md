# gxcg-spider
爬取[gxcg网](http://www.ccgp-guangxi.gov.cn)招投标公告

## 功能介绍
爬取网站公告内容，支持关键字搜索，起始和结束时间查询。
+ 客户端模式：结果输出到excel表格
+ 服务端模式：提供页面查询和结果excel表格下载

## 爬取分类
支持以下分类的公告爬取：
+ 中标成交结果公告

## 使用示例
### 客户端模式
```buildoutcfg
执行：python spider_client.py -c 0 -k 社会福利院 -s 2021-12-01 -e 2023-04-20
或者：gxcg_spider_tool.exe -c 0 -k 社会福利院 -s 2021-12-01 -e 2023-04-20
输出：中标成交结果公告-社会福利院-时间(2021-12-01~2023-04-20).xlsx
```
```commandline
生成exe：pyinstaller -p ./result_win_bid.py ./spider_category.py -F ./spider_client.py -i ./doc/ico/spider32.ico -n gxcg_spider_tool

生成exe并添加dll：pyinstaller -p ./result_win_bid.py ./spider_category.py -F ./spider_client.py -i ./doc/ico/spider32.ico -n gxcg_spider_tool --add-data "./dll/api-ms-win-core-path-l1-1-0.dll;."
```
### 服务端模式
```buildoutcfg
搭建docker环境，执行docker-start.sh
访问：http://127.0.0.1:8765
```
### 其他
```commandline
导出依赖：pip freeze > requirements.txt
导入依赖：pip install -r requirements.txt
```

## 声明
爬取的所有公告数据均已在网站公开，本工具仅做学习交流使用。
