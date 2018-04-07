# -*- coding: utf-8 -*-

import scrapy

class MeiZiTuItem(scrapy.Item):
    imagetitle1 = scrapy.Field()
    imagetitle2 = scrapy.Field()
    imagename = scrapy.Field()
    imageurl = scrapy.Field()
    url = scrapy.Field()

class LyricItem(scrapy.Item):
    songid = scrapy.Field()
    singermid = scrapy.Field()
    singer = scrapy.Field()
    song = scrapy.Field()
    lyric = scrapy.Field()

class CommentTotalItem(scrapy.Item):
    songid = scrapy.Field()
    singermid = scrapy.Field()
    commentcount = scrapy.Field()

class CommentItem(scrapy.Item):
    songid = scrapy.Field()
    singermid = scrapy.Field()
    commentid = scrapy.Field()
    content = scrapy.Field()
    userid = scrapy.Field()
    likecount = scrapy.Field()
    ishot = scrapy.Field()

