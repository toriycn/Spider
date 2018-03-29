# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from Spider.items import IdiomItem

class IdiomSpider(scrapy.Spider):
    name = 'idiom'
    # allowed_domains = ['https://www.baidu.com/']
    # start_urls = ['https://chengyu.911cha.com/zishu_4.html']

    def start_requests(self):
        for i in range(18):
            url = 'https://chengyu.911cha.com/zishu_4_p%s.html'%(i+2)
            yield Request(url,self.parse)

    def parse(self, response):
        for li in response.xpath('/html/body/div[2]/div[1]/div[2]/div[5]/ul/li'):
            idiom = li.xpath('a/text()').extract()
            yield {'idiom':idiom}
