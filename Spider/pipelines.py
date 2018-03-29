# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from Spider.items import IdiomItem

class DemospiderPipeline(object):
    def process_item(self, item, spider):
        if isinstance(item,IdiomItem):
            print(item.idiom)
