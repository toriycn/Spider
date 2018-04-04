# -*- coding: utf-8 -*-

import scrapy
from scrapy.http import Request
import re
import json
import logging
from Spider.items import SongItem

class QqmusicSpider(scrapy.Spider):
    # 歌手的mid，在qq音乐中打开歌手页面，连接中singer后面即为mid
    # 如https://y.qq.com/n/yqq/singer/004KKLWZ4320g1.html，id为004KKLWZ4320g1
    singermids = ['004KKLWZ4320g1']
    # 每次获取歌曲个数
    num = 30

    name = 'qqmusic'

    def start_requests(self):
        for singermid in QqmusicSpider.singermids:
            url = self.getSongsUrl(singermid, 0, QqmusicSpider.num)
            print(url)
            yield Request(url, callback=self.parse, meta={'begin': 0, 'singermid': singermid})

    def parse(self, response):
        datajson = json.loads(response.body_as_unicode())
        data = datajson['data']
        singername = data['singer_name']
        begin = response.meta.get('begin', None) + 30
        singermid = response.meta.get('singermid', None)
        # 如果当前页面不满30，说明已到结尾，否则继续请求
        if len(data['list']) is 30:
            url = self.getSongsUrl(singermid, begin, QqmusicSpider.num)
            yield Request(url, callback=self.parse, meta={'begin': begin, 'singermid': singermid})

        for songinfo in data['list']:
            musicdata = songinfo['musicData']
            referer = 'https://y.qq.com/n/yqq/song/%s.html' % (singermid)
            url = self.getLyricUrl(musicdata['songid'])
            songname = musicdata['songname']
            yield Request(url, callback=self.parse_lyric,
                          meta={'referer': referer, 'songname': songname, 'singername': singername})

    def parse_lyric(self, response):
        # 作者
        singername = response.meta.get('singername', None)
        # 歌曲名称
        songname = response.meta.get('songname', None)
        # 返回的body
        datastr = response.body_as_unicode()
        # 将返回的body处理成json格式
        pattern = re.compile(r'{.*}')
        jsons = pattern.findall(datastr)
        lyricinfo = json.loads(jsons[0])
        # 根据返回状态码判断歌词获取是否成功
        if lyricinfo['retcode'] is 0:
            # 歌词
            lyric = self.formatlyric(lyricinfo['lyric'])

            item = SongItem()
            item['singer'] = singername
            item['song'] = songname
            item['lyric'] = lyric

            yield item
        else:
            logging.error("获取歌曲<%s>歌词失败，返回结果：%s" % (songname, datastr))

    # 获取歌手单曲列表的接口地址 singermid 歌手的mid  begin 开始位置 num 获取歌曲个数
    def getSongsUrl(self, singermid, begin, num):
        url = 'https://c.y.qq.com/v8/fcg-bin/fcg_v8_singer_track_cp.fcg?g_tk=5381&format=jsonp&' \
              'inCharset=utf8&outCharset=utf-8&platform=yqq&singermid=%s&order=listen&begin=%s&num=%s&' \
              'songstatus=1' % (singermid, begin, num)
        return url

    # 获取歌词接口
    def getLyricUrl(self,songid):
        url = 'https://c.y.qq.com/lyric/fcgi-bin/fcg_query_lyric.fcg?nobase64=1&musicid=%s&callback=jsonp1&' \
              'g_tk=5381&jsonpCallback=jsonp1&loginUin=0&hostUin=0&format=jsonp&inCharset=utf8&' \
              'outCharset=utf-8&notice=0&platform=yqq&needNewCode=0' % (songid)
        return url

    # 格式化歌词
    def formatlyric(self, lyric):
        # 去除歌词中所有[]中内容
        f1 = re.sub(r'\[(.*?)\]', '', lyric)
        # 去除歌词中所有‘&#+数字’
        f2 = re.sub(r'&#\d{2,};', ';', f1)
        # 去除重复；
        f3 = re.sub(r';{2,}', ';', f2)
        # 去除标题，作者等信息，（效果有待改进）
        f4 = re.sub(r'^(.*?)曲：(.*?);', '', f3)
        return f4