import jieba.analyse
import result_win_bid

# 模拟浏览器请求头
HEADERS = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 4.2.1; en-us; Nexus 4 Build/JOP40D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166 Mobile Safari/535.19",
        "Content-Type": "application/json",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9", "Accept": "*/*"}
# br换行符替换标记
HTML_BR_REPLACE_TARGET = 'wjy'
# 进度条展示开关
PROGRESS_BAR_DISABLE = False
# 数据库文件路径
DB_PATH = 'data/sqlite3/spider.db'
# excel文件导出路径
EXCEL_OUT_PUT_DIR = './output/'
# 公告分类字典
SPIDER_CATEGORY = {'0': result_win_bid}
# 分词自定义字典文件路径
DIC_FILE_PATH = './data/jieba/dict.txt'
# 分词自定义词频文件路径
IDF_FILE_PATH = './data/jieba/idf.txt'

# TODO 使用结巴分词抽取标题里的机构名称。使用自定义字典和词频
def get_category_name_by_title(title=''):
    # jieba.load_userdict(DIC_FILE_PATH)
    # jieba.cut(title)
    jieba.analyse.set_idf_path(IDF_FILE_PATH)
    return jieba.analyse.extract_tags(title, topK=1)[0]