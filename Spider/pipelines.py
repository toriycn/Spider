# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.pipelines.images import ImagesPipeline
from scrapy import Request
from scrapy.exceptions import DropItem
import re

#     def __init__(self):
#         self.db = pymysql.connect(settings.MYSQL_URL, settings.MYSQL_USER_NAME,
#                       settings.MYSQL_USER_PSD, settings.MYSQL_DB_NAME, charset='utf8', use_unicode=True)
#         self.cursor = self.db.cursor()
#
#     def insert(self, item):
#         if isinstance(item, IdiomItem):
#             sql = "INSERT INTO idiom (idiom) VALUES ('%s')" % (item['idiom'])
#             self.cursor.execute(sql)
#             self.db.commit()

# 自定义图片下载管道
class MyImagePipeline(ImagesPipeline):

    # 从item中获取图片url并返回
    def get_media_requests(self, item, info):
        url = item['imageurl']
        yield Request(url, meta={'item': item, 'referer': item['url']})

    def item_completed(self, results, item, info):
        image_paths = [x['path'] for ok, x in results if ok]
        if not image_paths:
            raise DropItem("Item contains no images")
        return item

    def file_path(self, request, response=None, info=None):
        item = request.meta['item']  # 通过上面的meta传递过来item

        filename = u'{0}/{1}/{2}'.format(self.clearpath(item['imagetitle1']),
                                         self.clearpath(item['imagetitle2']),
                                         self.clearpath(item['imagename']+'.jpg'))
        return filename

    def clearpath(self,path):
        """
        :param path: 需要清洗的文件夹名字
        :return: 清洗掉系统非法文件夹名字的字符串
        """
        path = re.sub(r'[？\\*|“<>:/]', '', str(path))
        return path
