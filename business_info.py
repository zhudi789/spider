# coding: utf-8
"""
author: wanghongjun
date: 2020.2.24
"""
import requests, threading
from urllib import parse
from bs4 import BeautifulSoup
import time, datetime
import pandas as pd
import random
import os
import sys

class business_info(object):
    # 初始化参数
    def __init__(self):
        self.base_url = "https://www.qichacha.com"

    def write(self, path, text):
        with open(path, 'a', encoding='utf-8') as f:
            f.writelines(text)
            f.write('\n')
            f.close()

    def truncatefile(self, path):
        with open(path, 'w', encoding='utf-8') as f:
            f.truncate()

    def read(self, path):
        with open(path, 'r', encoding='utf-8') as f:
            txt = []
            for s in f.readlines():
                txt.append(s.strip())
        return txt

    def gettimediff(self, start, end):
        seconds = (end - start).seconds
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        diff = ("%02d:%02d:%02d" % (h, m, s))
        return diff

    def getheaders(self):
        user_agent_list = [ \
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1" \
            "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11", \
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6", \
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6", \
            "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1", \
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5", \
            "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5", \
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3", \
            "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3", \
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3", \
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3", \
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3", \
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3", \
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3", \
            "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3", \
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3", \
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24", \
            "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
        ]
        UserAgent = random.choice(user_agent_list)
        headers = {'User-Agent': UserAgent}
        return headers

    def checkip(self, targeturl, ip):
        headers = self.getheaders()  # 定制请求头
        proxies = {"http": "http://" + ip, "https": "http://" + ip}  # 代理ip
        try:
            response = requests.get(url=targeturl, proxies=proxies, headers=headers, timeout=5).status_code
            if response == 200:
                return True
            else:
                return False
        except:
            return False

    def findip(self, type, pagenum, targeturl, path):  # ip类型,页码,目标url,存放ip的路径
        list = {'1': 'http://www.xicidaili.com/wn/',  # xicidaili国内https代理
                '2': 'http://www.xicidaili.com/nn/',  # xicidaili国内高匿代理
                '3': 'http://www.xicidaili.com/nt/',  # xicidaili国内普通代理
                '4': 'http://www.xicidaili.com/wt/'}  # xicidaili国外http代理
        url = list[str(type)] + str(pagenum)  # 配置url
        # print("url:",url)
        headers = self.getheaders()  # 定制请求头
        html = requests.get(url=url, headers=headers, timeout=5).text
        # print("html:", html)
        soup = BeautifulSoup(html, 'lxml')
        all = soup.find_all('tr', class_='odd')
        for i in all:
            t = i.find_all('td')
            ip = t[1].text + ':' + t[2].text
            is_avail = self.checkip(targeturl, ip)
            if is_avail == True:
                self.write(path=path, text=ip)
                print(ip)

    def getip(self, targeturl, path):
        self.truncatefile(path)  # 爬取前清空文档
        start = datetime.datetime.now()  # 开始时间
        threads = []
        for type in range(1):  # 四种类型ip,每种类型取前三页,共12条线程
            for pagenum in range(3):
                t = threading.Thread(target=self.findip, args=(type + 1, pagenum + 1, targeturl, path))
                threads.append(t)
        print('开始爬取代理ip')
        for s in threads:  # 开启多线程爬取
            s.start()
        for e in threads:  # 等待所有线程结束
            e.join()
        print('爬取完成')
        end = datetime.datetime.now()  # 结束时间
        diff = self.gettimediff(start, end)  # 计算耗时
        ips = self.read(path)  # 读取爬到的ip数量
        print('一共爬取代理ip: %s 个,共耗时: %s \n' % (len(ips), diff))

    def post_header(self, re):
        t = datetime.datetime.now()
        timeArray = time.strptime(str(t).split('.')[0], "%Y-%m-%d %H:%M:%S")
        timeStamp = int(time.mktime(timeArray))
        headers = {
            'Host': 'www.qichacha.com',
            'Connection': 'keep-alive',
            'Accept': r'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': r'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.116 Safari/537.36',
            'Referer': re,
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cookie': 'UM_distinctid=16e826e23d3de-0a09e4426506fb-7711a3e-100200-16e826e23d44d; zg_did=%7B%22did%22%3A%20%2216e826e2b5f124-0a9cc15d1ea268-7711a3e-100200-16e826e2b606f%22%7D; _uab_collina=157414628924656066083556; QCCSESSID=2rdci6gdcbfbpgsm59glfit596; acw_tc=71cf212315820748870458194ee820afeec975dc24d0ce90fe28b84cba; hasShow=1; Hm_lvt_3456bee468c83cc63fb5147f119f1075=1582181572,1582185680,1582256042,1582507877; CNZZDATA1254842228=1632500605-1574142938-https%253A%252F%252Fsp0.baidu.com%252F%7C1582526790; zg_de1d1a35bfa24ce29bbf2c7eb17e6c4f=%7B%22sid%22%3A%201582527600664%2C%22updated%22%3A%201582529984458%2C%22info%22%3A%201582074885951%2C%22superProperty%22%3A%20%22%7B%7D%22%2C%22platform%22%3A%20%22%7B%7D%22%2C%22utm%22%3A%20%22%7B%7D%22%2C%22referrerDomain%22%3A%20%22www.qichacha.com%22%2C%22zs%22%3A%200%2C%22sc%22%3A%200%2C%22cuid%22%3A%20%22b474454900342015dc3fdbc10d8f7fa0%22%7D; Hm_lpvt_3456bee468c83cc63fb5147f119f1075=' + str(
                timeStamp),
        }
        return headers

    def start_up_browser(self, re, one_keyWords, keyWords_list_copy, proxies):
        s = requests.Session()
        try:
            response = s.get(re, headers=self.getheaders(), proxies=proxies)
            time.sleep(10)
            soup = BeautifulSoup(response.text, 'lxml')
            # print(response.text)
            # 进入企业详细页面
            try:
                business = soup.find_all(class_='ma_h1')[0]['href']
                # print(business)
                # print(self.base_url+"/cbase"+business[5:])
                # 获取企业详细页面信息
                try:
                    next_url = self.base_url+"/cbase"+business[5:]
                    time.sleep(10)
                    business_res = s.get(next_url, headers=self.getheaders(), proxies=proxies)
                    # print(business_res.text)
                    # 保存html文件
                    f = open('html_file\\' + one_keyWords + '.html', 'w', encoding="utf-8")
                    for i in business_res.text:
                        f.write(i)
                    f.close()
                    keyWords_list_copy.remove(one_keyWords)
                except:
                    print("获取页面res失败...")
            except:
                print("没有对应元素...")
        except Exception:
            print('企查查页面访问失败...')

    # 解析html文件
    def analysis_html(self, html_res, data):
        soup_business = BeautifulSoup(html_res, 'lxml')
        try:
            business_1 = soup_business.find_all(colspan=3)
            business_address_ = business_1[0].get_text()
            address = str(business_address_).split('\n')[1].strip(' ')
            data.append(address)

            business_scope = business_1[1].get_text()
            scope = str(business_scope).split('\n')[1].strip(' ')
            data.append(scope)
        except:
            data.append(None)
            data.append(None)

        try:
            business_corporate = soup_business.find(class_="seo font-20")
            corporate = business_corporate.get_text()
            data.append(corporate)
            # print(corporate)
        except:
            data.append(None)

        # 主要人员信息
        try:
            all_main_person = soup_business.select("table[class='ntable ntable-odd'] tr")
            columns_name = all_main_person[0].select("th")
            columns_name_list = [one.get_text() for one in columns_name][1:]
            # print(columns_name_list)
            list_mainPerson = []
            for i in range(1, len(all_main_person) - 1, 2):
                name_h3 = all_main_person[i].find_all("h3")
                if len(name_h3) > 0:
                    name = all_main_person[i].select("h3")[0].get_text()
                    # print(name)
                post = all_main_person[i].select("td[class='text-center']")
                if len(post) > 0:
                    post_list = [one_post.get_text() for one_post in post]
                    post_list_r = [two_post.strip('\n').strip(' ').rstrip('\n') for two_post in post_list]
                    # print(post_list_r)
                    post_res = post_list_r[columns_name_list.index("职务") - 1]
                if [name, post_res] not in list_mainPerson:
                    list_mainPerson.append([name, post_res])
                # print(name, post_res)
                # break
            mainPerson = '\n'.join(one[0] + ' ' + one[1] for one in list_mainPerson)
            data.append(mainPerson)
            # print(list_mainPerson)
        except:
            data.append(None)

        # 变更信息
        try:
            change_info = soup_business.select("section[id='Changelist']")
            # change_columnsName = change_info[0].select("th")
            # change_columnsName_r = [one.get_text() for one in change_columnsName]
            # print(change_columnsName_r)
            change_info = change_info[0].select("table[style='margin-bottom: -1px;'] tr")
            list_change = []
            res_list_change = []
            for one_change in change_info:
                data_change = []
                change_info_td = one_change.select("td")
                for one_change_td in change_info_td:
                    change_text = one_change_td.get_text()
                    change_text = change_text.lstrip('\n')
                    change_text = change_text.strip(' ')
                    change_text = change_text.rstrip('\n')
                    change_text = change_text.lstrip('\n')
                    change_text = change_text.replace('\n', '。')
                    change_text = change_text.replace(' ', '')
                    data_change.append(change_text)
                # print(data_change)
                list_change.append('  '.join(one for one in data_change))
                # break
            res_list_change.append('\n'.join(two for two in list_change))
            # print(res_list_change)
            # print(res_list_change[0])
            data.append(res_list_change[0])
        except:
            data.append(None)


# keyWords_list = ["深圳市腾讯计算机系统有限公司", "马上消费金融股份有限公司"]
df = pd.read_excel('企业.xlsx', encoding='utf-8')
keyWords_list = [one[0] for one in df.values.tolist()]
keyWords_list_copy = keyWords_list.copy()

one_business = business_info()

# 免费ip获取
path = 'ip.txt'  # 存放爬取ip的文档path
targeturl = 'https://www.qichacha.com/'  # 验证ip有效性的指定url
one_business.getip(targeturl, path)

f_ip = open('ip.txt', 'r')
ip_agent = [one_ip.strip('\n') for one_ip in f_ip.readlines()]
# print(ip_agent)
# print(ip_agent[random.randint(0, len(ip_agent)-1)])

for i in range(1):
    for one_keyWords in keyWords_list:
        proxy = ip_agent[random.randint(0, len(ip_agent)-1)]
        print("当前ip：", proxy)
        proxies = {'http': 'http://' + proxy, 'https': 'https://' + proxy}
        re = "https://www.qichacha.com/search?key=" + parse.quote(one_keyWords)
        one_business.start_up_browser(re, one_keyWords, keyWords_list_copy, proxies)
        time.sleep(30)
    print("所有html文件保存完成...")

    pd.DataFrame(keyWords_list_copy).to_excel("未完成html抓取名单.xlsx", encoding='gbk', index=False, header=False)

    # 解析html文件
    # data = []
    # all_html = os.listdir('./html_file')
    # for one_html in all_html:
    #     r_oneHtml = open('./html_file' + '/' + one_html, 'r', encoding="utf-8").read()
    #     one_data = []
    #     print(one_html.split('.')[0])
    #     one_data.append(one_html.split('.')[0])
    #     one_business.analysis_html(r_oneHtml, one_data)
    #     data.append(one_data)
    #     # break
    # # pd.DataFrame(data, columns=["公司名称", "地址", "经营范围", "法人", "主要人员信息", "变更信息"]).\
    # #     to_excel("business_info2.xlsx", encoding='gbk', index=False)

