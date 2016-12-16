# -*- coding: utf-8 -*-
"""models"""
from xml.dom import minidom
import collections
import time
import sys
import xmltodict

if sys.version > "3":
    long = int
    unicode = str


def kv2element(key, value, doc):
    """kv2element"""
    if value is None:
        return None
    ele = doc.createElement(key)
    if isinstance(value, str) or isinstance(value, unicode):
        data = doc.createCDATASection(value)
        ele.appendChild(data)
    else:
        text = doc.createTextNode(str(value))
        ele.appendChild(text)
    return ele


def fields2elements(tuples, enclose_tag=None, doc=None):
    """fields2elements"""
    if enclose_tag:
        xml = doc.createElement(enclose_tag)
        for key in tuples._fields:
            ele = kv2element(key, getattr(tuples, key), doc)
            if ele is not None:
                xml.appendChild(ele)
        return xml
    else:
        return [kv2element(key, getattr(tuples, key), doc)
                for key in tuples._fields]


class WxRequest(object):
    """WxRequest"""

    def _parse(self, dicts):
        """parse dict"""
        if dicts is not None:
            for key, value in dicts.items():
                if isinstance(value, dict):
                    self._parse(value)
                else:
                    self.__dict__.update({key: value})

    def __init__(self, xml=None):
        if xml is not None:
            doc = xmltodict.parse(xml).get('xml', None)
            self._parse(doc)


class WxResponse(object):
    """WxResponse"""
    MsgType = 'text'

    def __init__(self, request):
        self.CreateTime = long(time.time())
        self.ToUserName = request.FromUserName
        self.FromUserName = request.ToUserName
        self.Extra = {}

    def content_nodes(self, doc):
        """content nodes base"""
        return

    def as_xml(self):
        """as_xml"""
        doc = minidom.Document()
        xml = doc.createElement('xml')
        doc.appendChild(xml)
        xml.appendChild(kv2element('ToUserName', self.ToUserName, doc))
        xml.appendChild(kv2element('FromUserName', self.FromUserName, doc))
        xml.appendChild(kv2element('CreateTime', self.CreateTime, doc))
        xml.appendChild(kv2element('MsgType', self.MsgType, doc))
        contents = self.content_nodes(doc)
        if isinstance(contents, list) or isinstance(contents, tuple):
            for content in contents:
                xml.appendChild(content)
        else:
            xml.appendChild(contents)
        if self.Extra:
            if sys.version_info < (3, 0):
                for key, value in self.Extra.iteritems():
                    xml.appendChild(kv2element(key, value, doc))
            else:
                for key, value in self.Extra.items():
                    xml.appendChild(kv2element(key, value, doc))
        return doc.toxml()


WxMusic = collections.namedtuple('WxMusic', 'Title Description MusicUrl HQMusicUrl')
WxArticle = collections.namedtuple('WxArticle', 'Title Description PicUrl Url')
WxImage = collections.namedtuple('WxImage', 'MediaId')
WxVoice = collections.namedtuple('WxVoice', 'MediaId')
WxVideo = collections.namedtuple('WxVideo', 'MediaId Title Description')
WxLink = collections.namedtuple('WxLink', 'Title Description Url')


class WxEmptyResponse(WxResponse):
    """WxEmptyResponse"""

    def __init__(self):
        """init"""
        pass

    def as_xml(self):
        """as_xml"""
        return ''


class WxTextResponse(WxResponse):
    """WxTextResponse"""
    MsgType = 'text'

    def __init__(self, text, request):
        """init"""
        super(WxTextResponse, self).__init__(request)
        self.text = text

    def content_nodes(self, doc):
        """content_nodes"""
        return kv2element('Content', self.text, doc)


class WxCompoundResponse(WxResponse):
    """WxCompoundResponse"""
    MsgType = ''
    Tag = ''

    def __init__(self, data, request):
        """init"""
        super(WxCompoundResponse, self).__init__(request)
        self.data = data

    def content_nodes(self, doc):
        """content_nodes"""
        return fields2elements(self.data, self.Tag, doc)


class WxImageResponse(WxCompoundResponse):
    """WxImageResponse"""
    MsgType = 'image'
    Tag = 'Image'


class WxVoiceResponse(WxCompoundResponse):
    """WxVoiceResponse"""
    MsgType = 'voice'
    Tag = 'Voice'


class WxVideoResponse(WxCompoundResponse):
    """WxVideoResponse"""
    MsgType = 'video'
    Tag = 'Video'


class WxMusicResponse(WxResponse):
    """WxMusicResponse"""
    MsgType = 'music'
    Tag = 'Music'


class WxNewsResponse(WxResponse):
    """WxNewsResponse"""
    MsgType = 'news'

    def __init__(self, articles, request):
        """init"""
        super(WxNewsResponse, self).__init__(request)
        if isinstance(articles, list):
            self.articles = articles
        else:
            self.articles = [articles]

    def content_nodes(self, doc):
        """content_nodes"""
        count = kv2element('ArticleCount', len(self.articles), doc)
        articles = doc.createElement('Articles')
        for article in self.articles:
            articles.appendChild(fields2elements(article, 'item', doc))
        return count, articles


class APIError(object):
    """APIError"""

    def __init__(self, code, msg):
        """init"""
        self.code = code
        self.message = msg
