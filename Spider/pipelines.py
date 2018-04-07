# -*- coding: utf-8 -*-

from scrapy.pipelines.images import ImagesPipeline
from scrapy import Request
from scrapy.exceptions import DropItem
import re
import pymysql
from Spider import settings
from Spider.items import LyricItem
from Spider.items import CommentTotalItem
from Spider.items import CommentItem
from Spider.items import MeiZiTuItem

class QQMusicItemPipeline(object):
    def __init__(self):
        self.db = pymysql.connect(settings.MYSQL_URL, settings.MYSQL_USER_NAME,
                                  settings.MYSQL_USER_PSD, settings.MYSQL_DB_NAME, charset='utf8', use_unicode=True)
        self.cursor = self.db.cursor()

    def process_item(self, item, spider):
        if isinstance(item, LyricItem):
            # 查看数据库是否存在相同作者相同名称歌曲
            if len(self.selectLyricBySongId(item)) is 0:
                # 为0不存在，添加到数据库
                self.insertLyric(item)
        elif isinstance(item, CommentTotalItem):
            if len(self.selectCommentTotalBySongid(item)) is 0:
                self.insertCommentTotal(item)
        elif isinstance(item, CommentItem):
            if len(self.selectCommentByCommentId(item)) is 0:
                self.insertComment(item)
        else:
            return item

    def insertLyric(self, item):
        sql = 'INSERT INTO QQMusicLyric (songid, singermid, singer, song, lyric) VALUES ("%s", "%s", "%s", "%s", "%s")' % \
              (item['songid'], item['singermid'], item['singer'], item['song'], item['lyric'])
        self.cursor.execute(sql)
        self.db.commit()

    def selectLyricBySongId(self, item):
        sql = 'SELECT * FROM QQMusicLyric WHERE songid = "%s" ' % (item['songid'])
        self.cursor.execute(sql)
        results = self.cursor.fetchall()
        return results

    def insertCommentTotal(self, item):
        sql = 'INSERT INTO QQMusicCommentTotal (songid, singermid, commentcount) VALUES ("%s", "%s", %s)' \
              % (item['songid'], item['singermid'], item['commentcount'])
        self.cursor.execute(sql)
        self.db.commit()

    def selectCommentTotalBySongid(self, item):
        sql = 'SELECT * FROM QQMusicCommentTotal WHERE songid = "%s"' % (item['songid'])
        self.cursor.execute(sql)
        results = self.cursor.fetchall()
        return results

    def insertComment(self, item):
        sql = 'INSERT INTO QQMusicCommentList (songid, singermid, commentid, content, userid, likecount, ishot) ' \
              'VALUES ("%s","%s","%s","%s","%s","%s","%s")' % (item['songid'], item['singermid'], item['commentid']
            , item['content'], item['userid'], item['likecount'], item['ishot'])
        self.cursor.execute(sql)
        self.db.commit()

    def selectCommentByCommentId(self, item):
        sql = 'SELECT * FROM QQMusicCommentList WHERE commentid = "%s"' % (item['commentid'])
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
