# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from Spider.items import IdiomItem
import pymysql
from Spider import settings

class IdiomPipeline(object):

    def __init__(self):
        self.db = pymysql.connect(settings.MYSQL_URL, settings.MYSQL_USER_NAME, settings.MYSQL_USER_PSD, settings.MYSQL_DB_NAME, charset='utf8', use_unicode=True)
        self.cursor = self.db.cursor()

    def process_item(self, item, spider):
        if isinstance(item, IdiomItem):
            sql = "INSERT INTO idiom (idiom) VALUES ('%s')" % (item['idiom'])
            self.cursor.execute(sql)
            self.db.commit()
            return item
