# -*- coding: utf-8 -*-

import scrapy
from scrapy.http import Request
import re
import json
import logging
from Spider.items import LyricItem
from Spider.items import CommentTotalItem
from Spider.items import CommentItem

class QqmusicSpider(scrapy.Spider):
    # 歌手的mid，在qq音乐中打开歌手页面，连接中singer后面即为mid
    # 如https://y.qq.com/n/yqq/singer/004KKLWZ4320g1.html，id为004KKLWZ4320g1

    # 老狼，李志，宋冬野，赵雷，陈粒，谢春花，张玮玮，好妹妹乐队，陈鸿宇，王梵瑞，万能青年旅店，马頔，jam，
    # 钟立风，陈小熊，徐海俏，尧十三，周云蓬，贰佰，花粥，万晓利，丢火车乐队
    # 鹿先生乐队，纣王老胡，房东的猫，小闯，郝云，刘明汉，夏小虎，刘东明，齐一
    singermids = ['002N3lYO38w8Dp', '004KKLWZ4320g1', '001Lr98T0yEWAk', '004WgCsE3KBddt', '003hTTjo3JYqgM'
                  , '001SXl8y2mQobu', '0020IaUo4Vgsjk', '001kwvXz1vTlaP', '0023ni2j3F9CpN', '003Z8WjM23prlT'
                  , '003xkuV90Aswpy', '004WROsW0OjNeD', '0015E1aN3zm7tO', '003r4Mf04S5JMr', '00169imA4Iub3I'
                  , '000d55760WnzUf', '004S3vUn27fDYv', '004asIE70OvN4z', '000PeZCQ1i4XVs', '000Qz0Ta1vyzNn'
                  , '0044gacX2dLf6i', '000N6Y3P3KDGfE', '001TUnFo00FUzY', '0045itb20xVn75', '0013bmPw3PPzoB'
                  , '002Ua1Ph1SH8iF', '002pQHUo0XZO8V', '002WkEWV1TA75B', '003GTrdR2M8Dvd', '00481OfY48EFE7'
                  , '001w9wGT07vpJv']
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

        # 迭代获取歌曲id
        for songinfo in data['list']:
            musicdata = songinfo['musicData']
            referer = 'https://y.qq.com/n/yqq/song/%s.html' % (singermid)
            lyricurl = self.getLyricUrl(musicdata['songid'])
            commenttotalurl = self.getCommentTotal(musicdata['songid'])
            commentlisturl = self.getCommentList(musicdata['songid'])
            songname = musicdata['songname']
            yield Request(lyricurl, callback=self.parse_lyric,
                          meta={'referer': referer, 'songname': songname,
                                                    'singername': singername,
                                                    'songid': musicdata['songid'],
                                                    'singermid': singermid})
            yield Request(commenttotalurl, callback=self.parse_commenttotal, meta={'referer': referer, 'singermid': singermid})
            yield Request(commentlisturl, callback=self.parse_commentlist, meta={'referer': referer, 'singermid': singermid})


    def parse_lyric(self, response):
        # 作者
        singername = response.meta.get('singername', None)
        # 作者mid
        singermid = response.meta.get('singermid', None)
        # 歌曲名称
        songname = response.meta.get('songname', None)
        # 歌曲id
        songid = response.meta.get('songid', None)
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

            item = LyricItem()
            item['singer'] = singername
            item['song'] = songname
            item['lyric'] = lyric
            item['songid'] = songid
            item['singermid'] = singermid

            yield item
        else:
            logging.error("获取歌曲<%s>歌词失败，返回结果：%s" % (songname, datastr))

    def parse_commenttotal(self, response):
        # 作者mid
        singermid = response.meta.get('singermid', None)
        datastr = response.body_as_unicode()
        commenttotaljson = json.loads(datastr)
        if commenttotaljson['code'] is 0:
            item = CommentTotalItem()
            item['songid'] = commenttotaljson['topid']
            item['singermid'] = singermid
            item['commentcount'] = commenttotaljson['commenttotal']
            yield item
        else:
            logging.error("获取歌曲id:%s 的评论数失败，返回结果：%s" % (commenttotaljson['topid'], commenttotaljson['commenttotal']))

    def parse_commentlist(self, response):
        datastr = response.body_as_unicode()
        commentinfo = json.loads(datastr)
        songid = commentinfo['topid']
        singermid = response.meta.get('singermid', None)

        if commentinfo['code'] is 0:
            hotcomment = commentinfo['hot_comment']
            comment = commentinfo['comment']
            # 热评数量不为零
            if hotcomment['commenttotal'] is not 0:
                # 热评列表
                hotcommentlist = hotcomment['commentlist']
                # 迭代评论列表
                for c in hotcommentlist:
                    item = CommentItem()
                    item['songid'] = songid
                    item['singermid'] = singermid
                    item['commentid'] = c['rootcommentid']
                    item['content'] = c['rootcommentcontent']
                    item['userid'] = c['rootcommentuin']
                    item['likecount'] = c['praisenum']
                    item['ishot'] = c['is_hot_cmt']
                    yield item

            # 评论列表不为零
            if comment['commenttotal'] is not 0:
                commentlist = comment['commentlist']
                for c in commentlist:
                    item = CommentItem()
                    item['songid'] = songid
                    item['singermid'] = singermid
                    item['commentid'] = c['rootcommentid']
                    item['content'] = c['rootcommentcontent']
                    item['userid'] = c['rootcommentuin']
                    item['likecount'] = c['praisenum']
                    item['ishot'] = c['is_hot_cmt']
                    yield item


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

    # 获取歌曲评论数量接口
    def getCommentTotal(self, songid):
        url = 'https://c.y.qq.com/base/fcgi-bin/fcg_global_comment_h5.fcg?inCharset=utf8&outCharset=utf8' \
              '&platform=yqq&cid=205360772&reqtype=1&biztype=1&topid=%s&cmd=4&domain=qq.com' % (songid)
        return url

    # 获取歌曲评论列表
    def getCommentList(self,songid):
        url = 'https://c.y.qq.com/base/fcgi-bin/fcg_global_comment_h5.fcg?inCharset=utf8&outCharset=utf8&' \
              'platform=yqq&reqtype=2&biztype=1&topid=%s&cmd=8&pagesize=25' \
              '&lasthotcommentid=&domain=qq.com&ct=24&cv=101010' % (songid)
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