# pytest test_spider_category.py
import spider_category

def test_get_category_name_by_title():
    title = '南宁市建昶建设工程监理咨询有限责任公司关于南宁市社会福利院食堂食材配送采购项目的中标(成交)结果公告'
    category_name = spider_category.get_category_name_by_title(title)
    assert category_name == '社会福利院'