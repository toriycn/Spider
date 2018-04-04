# -*- coding: utf-8 -*-

from scrapy.pipelines.images import ImagesPipeline
from scrapy import Request
from scrapy.exceptions import DropItem
import re
import pymysql
from Spider import settings
from Spider.items import SongItem
from Spider.items import MeiZiTuItem

class QQMusicItemPipeline(object):
    def __init__(self):
        self.db = pymysql.connect(settings.MYSQL_URL, settings.MYSQL_USER_NAME,
                                  settings.MYSQL_USER_PSD, settings.MYSQL_DB_NAME, charset='utf8', use_unicode=True)
        self.cursor = self.db.cursor()

    def process_item(self, item, spider):
        if isinstance(item,SongItem):
            # 查看数据库是否存在相同作者相同名称歌曲
            if len(self.selectBySingerNameAndSongName(item)) is 0:
                # 为0不存在，添加到数据库
                self.insert(item)
        else:
            return item

    def insert(self, item):
        sql = 'INSERT INTO QQMusic (singer, song, lyric) VALUES ("%s", "%s", "%s")' % \
              (item['singer'], item['song'], item['lyric'])
        self.cursor.execute(sql)
        self.db.commit()

    def selectBySingerNameAndSongName(self, item):
        sql = 'SELECT * FROM QQMusic WHERE singer = "%s" AND song = "%s"' % (item['singer'], item['song'])
        self.cursor.execute(sql)
        results = self.cursor.fetchall()
        return results

# 自定义图片下载管道
class MyImagePipeline(ImagesPipeline):

    # 从item中获取图片url并返回
    def get_media_requests(self, item, info):
        if isinstance(item, MeiZiTuItem):
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
