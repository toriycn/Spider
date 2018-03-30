# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
from scrapy.downloadermiddlewares.httpproxy import HttpProxyMiddleware
import random

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

    def process_request(self, request, spider):
        # 调用接口获取ip
        ip = ''
        request.meta["proxy"] = "http://" + ip