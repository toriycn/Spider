# -*- coding: utf-8 -*-

from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
from scrapy.downloadermiddlewares.httpproxy import HttpProxyMiddleware
from scrapy.http import HtmlResponse
from selenium.common.exceptions import TimeoutException
import random
import requests
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from Spider import settings

# 产生随机USER_AGENT
class RandomUserAgentMiddleware(UserAgentMiddleware):

    def __init__(self, user_agent):
        self.user_agent = user_agent

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            user_agent=crawler.settings.get('MY_USER_AGENT')
        )

    def process_request(self, request, spider):
        agent = random.choice(self.user_agent)

        request.headers['User-Agent'] = agent

# 从ip池随机获取ip
class RandomIPMiddleware(HttpProxyMiddleware):
    def __init__(self, ip):
        self.ip = ip
        self.ips = self.getips();

    def process_request(self, request, spider):
        # 调用接口获取ip
        ip = self.getrandomip()
        request.meta["proxy"] = "http://" + ip

    def getips(self):
        #
        # 接口参数如下
        # types	int	0: 高匿,1:匿名,2 透明
        # protocol	int	0: http, 1 https, 2 http/https
        # count	int	数量
        # country	str	取值为 国内, 国外
        # area	str	地区
        #
        # param = {'type':'1','country':'国内','count':'5'}
        # ips = requests.get('http://localhost:8000',params=param)

        param = {'type': '1', 'country': '国内','count': '10'}
        ipsinfojson = requests.get('http://localhost:8000', params=param)
        ipsinfo = json.loads(ipsinfojson.text)
        ips = []
        for ipinfo in ipsinfo:
            ip = '%s:%s' % (ipinfo[0], ipinfo[1])
            ips.append(ip)
        return ips

    def getrandomip(self):
        ip = random.choice(self.ips)
        self.ips.remove(ip)
        if len(self.ips) is 0:
            self.ips = self.getips()
        return ip

# 添加referer处理防盗链
class DealReferer(object):
    def process_request(self, request, spider):
        referer = request.meta.get('referer', None)
        if referer:
            request.headers['referer'] = referer

# 使用selenium渲染页面,并返回response对象
class SeleniumMiddleware(object):
    # 初始化selenium
    def __init__(self):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        self.browser = webdriver.Chrome(options=options)
        self.browser.set_page_load_timeout(settings.TIME_OUT)
        self.browser.set_script_timeout(settings.TIME_OUT)

    def process_request(self, request):
        try:
            url = request.url
            self.browser.get(url)
            return HtmlResponse(url=request.url, body=self.browser.page_source, request=request, encoding='utf-8', status=200)
        except TimeoutException:
            return HtmlResponse(url=request.url, status=500, request=request)