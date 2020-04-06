# coding: utf-8
"""
author: wanghongjun
date: 2020.2.12
"""
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
import pandas as pd
import time


class ccgp(object):
    # 初始化参数
    def __init__(self, first_url, key_words, search_c, type, category, time_long, browser_driver_address):
        self.first_url = first_url
        self.key_words = key_words
        self.search_c = search_c
        self.type = type
        self.category = category
        self.time_long = time_long
        self.browser_driver_address = browser_driver_address

    def start_up_browser(self):
        options = webdriver.ChromeOptions()
        # options.add_argument("--start-maximized")  # 界面设置最大化
        # options.add_argument('--headless')  # 隐藏浏览器
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_argument(
            '--user-agent="Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Mobile Safari/537.36"')
        driver = ''
        try:
            driver = webdriver.Chrome(chrome_options=options, executable_path=self.browser_driver_address)
            driver.set_page_load_timeout(100)   # 超时设置
            driver.set_script_timeout(100)  #
            print("驱动成功...")
            # 打开浏览器
            try:
                driver.get(self.first_url)
                print("成功打开浏览器...")
                # 输入key_words
                try:
                    input = driver.find_element_by_id('kw')
                    input.send_keys(self.key_words)
                    button_title = driver.find_element_by_id(self.search_c)
                    button_title.click()

                    # 筛选
                    type_onclock = "//li[contains(@onclick," + "'" + str(self.type) + "'" + ")]"
                    driver.find_element_by_xpath(type_onclock).click()
                    category_onclock = "//li[contains(@onclick," + "'" + str(self.category) + "'" + ")]"
                    driver.find_element_by_xpath(category_onclock).click()
                    time_onclock = "//li[contains(@onclick," + "'" + str(self.time_long) + "'" + ")]"
                    driver.find_element_by_xpath(time_onclock).click()
                except NoSuchElementException:
                    print("No Element.")
            except TimeoutException:  # 捕获是否超时
                print("Time Out.")
        except WebDriverException as driver_error:
            print("驱动失败...")
            print(driver_error)

        return driver

    def spider_data(self, driver, data, page_num):
        html = driver.page_source
        soup = BeautifulSoup(html, "lxml")
        all_part = soup.find_all('ul', class_="vT-srch-result-list-bid")
        for one in all_part:
            all_li = one.find_all('li')
            for one_li in all_li:
                one_data = []
                title = one_li.find('a').get_text()
                text = one_li.find('p').get_text()
                time_ = one_li.find('span').get_text()
                time_split = [t.strip(' ') for t in time_.split('\n')]
                time_split_ = [t for t in time_split if t != '']

                one_data.append(title)
                one_data.append(text)
                one_data.append(time_split_[0])  # time
                one_data.append(time_split_[1].split('：')[1])  # 采购人
                one_data.append(time_split_[2].split('：')[1])  # 代理机构
                one_data.append(time_split_[3])  # 类型
                one_data.append(time_split_[4][1:])  # 地点
                one_data.append(time_split_[5][1:])  # 范围

                data.append(one_data)
        # print('data', len(data))
        # 递归
        page_num += 1
        onclock_botton = 'gopage(' + str(page_num) + ')'
        onclock_ = "//a[contains(@onclick, " + "'" + str(onclock_botton) + "'" + ")]"
        time.sleep(10)  # 爬取下一页休眠10秒
        if soup.find('a', class_="next"):  # 有下一页
            # time.sleep(10)  # 爬取下一页休眠10秒
            driver.find_element_by_xpath(onclock_).click()
            self.spider_data(driver, data, page_num)


search_dict = {"搜标题": 'doSearch1', "搜全文": 'doSearch2'}
type_dict = {"所有类型": 'bidTypeSel(0)', "公开招标": 'bidTypeSel(1)', "询价公告": 'bidTypeSel(2)', "竞争性谈判": 'bidTypeSel(3)',
             "单一来源": 'bidTypeSel(4)', "资格预审": 'bidTypeSel(5)', "邀请公告": 'bidTypeSel(6)', "中标公告": 'bidTypeSel(7)',
             "更正公告": 'bidTypeSel(8)', "其他公告": 'bidTypeSel(9)',  "竞争性磋商": 'bidTypeSel(10)', "成交公告": 'bidTypeSel(11)',
             "废标终止": 'bidTypeSel(12)'}
category_dict = {"所有类别": 'bidSortSel(0)', "中央公告": 'bidSortSel(1)', "地方公告": 'bidSortSel(2)'}
time_long_dict = {"今日": 'timeSel(0)', "近3日": 'timeSel(1)', "近1周": 'timeSel(2)', "近1月": 'timeSel(3)', "近3月": 'timeSel(4)',
                  "近半年": 'timeSel(5)', "指定时间": 'timeSel(6)'}

# 从参数文件读取各项参数信息
f = open("configure_table.txt", "r")
configure = f.read()
f.close()

configure_list = [one.strip() for one in configure.split('\n') if one.strip() != '']
key_index = configure_list.index('# 关键字搜索列表')
browser_driver_address_index = configure_list.index('# 浏览器驱动地址')

key_words_list = configure_list[key_index+1: browser_driver_address_index]
browser_driver_address = configure_list[browser_driver_address_index+1:][0]
# print(key_words_list)
# print(browser_driver_address)

first_url = r'http://www.ccgp.gov.cn/'
# res_data = []
for one_keyWord in key_words_list:
    one_ccgp = ccgp(first_url, one_keyWord, search_dict["搜标题"], type_dict["中标公告"], category_dict["所有类别"],
                    time_long_dict["近半年"], browser_driver_address)
    driver = one_ccgp.start_up_browser()
    res_data = []
    print("开始抓取数据...")
    one_ccgp.spider_data(driver, res_data, 1)
    print("抓取数据完成...")
    driver.close()  # 关闭浏览器
    print("成功关闭浏览器")
    pd.DataFrame(res_data, columns=["标题", "内容", "时间", "采购人", "代理机构", "类型", "地点", "范围"]).to_csv(one_keyWord + '.csv',
                                                                                               encoding='gbk',
                                                                                               index=False)
    print("数据保存完成!")
    # res_data.append(["标题", "内容", "时间", "采购人", "代理机构", "类型", "地点", "范围"])
    time.sleep(60)

