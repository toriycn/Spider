# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from Spider.items import IdiomItem

class SpiderPipeline(object):
    def process_item(self, item, spider):
        if isinstance(item,IdiomItem):
            print("=======================================")
            print(item['idiom'])
