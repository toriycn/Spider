# -*- coding: utf-8 -*-

import scrapy

class MeiZiTuItem(scrapy.Item):
    imagetitle1 = scrapy.Field()
    imagetitle2 = scrapy.Field()
    imagename = scrapy.Field()
    imageurl = scrapy.Field()
    url = scrapy.Field()

class SongItem(scrapy.Item):
    singer = scrapy.Field()
    song = scrapy.Field()
    lyric = scrapy.Field()

