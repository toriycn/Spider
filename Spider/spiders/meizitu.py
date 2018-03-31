# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from Spider.items import MeiZiTuItem

class MeizituSpider(scrapy.Spider):
    name = 'meizitu'
    start_urls = ['http://www.meizitu.com/a/pure.html','http://www.meizitu.com/a/cute.html',
                  'http://www.meizitu.com/a/sexy.html','http://www.meizitu.com/a/fuli.html',
                  'http://www.meizitu.com/a/legs.html','http://www.meizitu.com/a/rixi.html',
                  'http://www.meizitu.com/a/yundong.html','http://www.meizitu.com/tag/mote_6_1.html',
                  'http://www.meizitu.com/tag/keai_64_1.html','http://www.meizitu.com/tag/qizhi_53_1.html',
                  'http://www.meizitu.com/tag/banluo_5_1.html','http://www.meizitu.com/tag/nvshen_460_1.html',
                  'http://www.meizitu.com/tag/quanluo_4_1.html','http://www.meizitu.com/tag/meitun_42_1.html',
                  'http://www.meizitu.com/tag/chengshu_487_1.html']

    def parse(self, response):
        # 获取页面下方翻页的所有href属性
        for href in response.xpath('//*[@id="wp_page_numbers"]/ul/li/a'):
            # 获取href文本
            url = href.xpath('@href').extract_first()
            # 将href拼成完整的url
            if url.startswith('/tag'):
                url = 'http://www.meizitu.com%s' % (url)
            else:
                url = 'http://www.meizitu.com/a/%s' % (url)
            yield Request(url,callback=self.parse_set)

    def parse_set(self,response):
        title1 = response.xpath('//*[@id="maincontent"]/div[1]/div/h3/text()[2]').extract_first()
        for setli in response.xpath('//*[@id="maincontent"]/div[1]/ul/li'):
            seturl = setli.xpath('div/h3/a/@href').extract_first()
            yield Request(seturl, callback=self.parse_pic, meta={'title1': title1})

    def parse_pic(self, response):
        url = str(response.url)
        title2 = response.xpath('//*[@id="maincontent"]/div[1]/div[1]/h2/a/text()').extract_first()
        for img in response.xpath('//*[@id="picture"]/p/img'):
            item = MeiZiTuItem()
            item['imagetitle1'] = response.meta['title1']
            item['imagetitle2'] = title2
            item['imagename'] = img.xpath('@alt').extract_first()
            item['imageurl'] = img.xpath('@src').extract_first()
            item['url'] = url
            yield item
