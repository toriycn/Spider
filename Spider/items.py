# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class MeiZiTuItem(scrapy.Item):
    imagetitle1 = scrapy.Field()
    imagetitle2 = scrapy.Field()
    imagename = scrapy.Field()
    imageurl = scrapy.Field()
    url = scrapy.Field()

