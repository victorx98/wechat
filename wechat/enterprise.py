# -*- coding: utf-8 -*-
"""enterprise"""
import time
import urllib
import sys
import requests
from .models import WxRequest, WxResponse
from .models import WxArticle, WxImage, WxVoice, WxVideo, WxLink
from .models import WxTextResponse, WxImageResponse, WxVoiceResponse, \
    WxVideoResponse, WxNewsResponse, APIError, WxEmptyResponse
from .official import WxApplication as BaseApplication, WxBaseApi
from .crypt import WXBizMsgCrypt

__all__ = ['WxRequest', 'WxResponse', 'WxArticle', 'WxImage',
           'WxVoice', 'WxVideo', 'WxLink', 'WxTextResponse',
           'WxImageResponse', 'WxVoiceResponse', 'WxVideoResponse',
           'WxNewsResponse', 'WxApplication',
           'WxApi', 'APIError']


class WxApplication(BaseApplication):
    """Wechat Application"""
    UNSUPPORT_TXT = u'暂不支持此类型消息'
    WELCOME_TXT = u'你好！感谢您的关注！'
    SECRET_TOKEN = None
    CORP_ID = None
    ENCODING_AES_KEY = None

    def process(self, params, xml=None, token=None, corp_id=None,
                aes_key=None):
        """process"""
        self.token = token or self.SECRET_TOKEN
        self.corp_id = corp_id or self.CORP_ID
        self.aes_key = aes_key or self.ENCODING_AES_KEY

        assert self.token is not None
        assert self.corp_id is not None
        assert self.aes_key is not None

        timestamp = params.get('timestamp', '')
        nonce = params.get('nonce', '')
        msg_signature = params.get('msg_signature', '')
        echostr = params.get('echostr', '')

        cpt = WXBizMsgCrypt(self.token, self.aes_key, self.corp_id)

        if not xml:
            err, echo = cpt.verify_url(msg_signature, timestamp, nonce, echostr)
            if err:
                return 'invalid request, code %s' % err
            else:
                return echo

        err, xml = cpt.decrypt_msg(xml, msg_signature, timestamp, nonce)
        if err:
            return 'decrypt message error , code %s' % err

        self.req = WxRequest(xml)
        func = self.handler_map().get(self.req.MsgType, None)
        if not func:
            return WxEmptyResponse()
        self.pre_process()
        rsp = func(self.req)
        self.post_process()
        result = rsp.as_xml().encode('UTF-8')

        if not result:
            return ''

        err, result = cpt.encrypt_msg(result, nonce)
        if err:
            return 'encrypt message error , code %s' % err
        return result


def format_list(data):
    """format list"""
    if data and (isinstance(data, list) or isinstance(data, tuple)):
        return '|'.join(data)
    else:
        return data


def simplify_send_parmas(params):
    """simplify send parmas"""
    keys = params.keys()
    for key in keys:
        if not params[key]:
            del params[key]
    return params


class WxApi(WxBaseApi):
    """Wechat Api"""
    API_PREFIX = 'https://qyapi.weixin.qq.com/'

    def __init__(self, appid, appsecret, api_entry=None):
        super(WxApi, self).__init__(appid, appsecret, api_entry)
        self.expires_in = time.time()
        self._access_token = None

    @property
    def access_token(self):
        """access token"""
        if self._access_token and time.time() >= self.expires_in:
            self._access_token = None

        if not self._access_token:
            token, err = self.get_access_token()
            if not err:
                self._access_token = token['access_token']
                self.expires_in = time.time() + token['expires_in']
                return self._access_token
            else:
                return None
        return self._access_token

    def get_access_token(self, url=None, **kwargs):
        """get access token"""
        params = {'corpid': self.appid, 'corpsecret': self.appsecret}
        params.update(kwargs)
        rsp = requests.get(url or self.api_entry + 'cgi-bin/gettoken',
                           params=params,
                           verify=WxBaseApi.VERIFY)
        return self._process_response(rsp)

    def departments(self):
        """departments"""
        return self._get('cgi-bin/department/list')

    def add_department(self, name, parentid='1', order=None):
        """add department"""
        params = {'name': name, 'parentid': parentid, 'order': order}
        return self._post('cgi-bin/department/create', params=params)

    def update_department(self, depid, name=None, parentid=None, order=None):
        """update department"""
        params = {'id': depid, 'name': name, 'parentid': parentid, 'order': order}
        return self._post('cgi-bin/department/update', params=params)

    def delete_department(self, depid):
        """delete department"""
        params = {'id': depid}
        return self._get('cgi-bin/department/delete', params=params)

    def tags(self):
        """tags"""
        return self._get('cgi-bin/tag/list')

    def add_tag(self, tagname):
        """add tag"""
        params = {'tagname': tagname}
        return self._post('cgi-bin/tag/create', params=params)

    def update_tag(self, tagid, tagname):
        """update tag"""
        params = {'tagid': tagid, 'tagname': tagname}
        return self._post('cgi-bin/tag/update', params=params)

    def delete_tag(self, tagid):
        """delete tag"""
        params = {'tagid': tagid}
        return self._get('cgi-bin/tag/delete', params=params)

    def tag_users(self, tagid):
        """tag users"""
        params = {'tagid': tagid}
        return self._get('cgi-bin/tag/get', params=params)

    def add_tag_user(self, tagid, userlist):
        """add tag user"""
        return self._post('cgi-bin/tag/addtagusers',
                          {'tagid': tagid, 'userlist': userlist})

    def remove_tag_user(self, tagid, userlist):
        """remove tag user"""
        return self._post('cgi-bin/tag/deltagusers', {'tagid': tagid, 'userlist': userlist})

    def department_users(self, department_id, fetch_child=0, status=0):
        """department users"""
        params = {'department_id': department_id, 'fetch_child': fetch_child, 'status': status}
        return self._get('cgi-bin/user/simplelist', params=params)

    def add_user(self, userid, name, department=None, position=None,
                 mobile=None, gender=None, tel=None, email=None,
                 weixinid=None, extattr=None):
        """add user"""
        params = {
            "userid": userid, "name": name, "department": department, "position": position,
            "mobile": mobile, "gender": gender, "tel": tel, "email": email, "weixinid": weixinid,
            "extattr": extattr,
        }
        return self._post('cgi-bin/user/create', params)

    def update_user(self, userid, name, department=None, position=None,
                    mobile=None, gender=None, tel=None, email=None,
                    weixinid=None, extattr=None):
        """update user"""
        params = {
            "userid": userid, "name": name, "department": department, "position": position,
            "mobile": mobile, "gender": gender, "tel": tel, "email": email, "weixinid": weixinid,
            "extattr": extattr,
        }
        return self._post('cgi-bin/user/update', params)

    def delete_user(self, userid):
        """delete user"""
        params = {'userid': userid}
        return self._get('cgi-bin/user/delete', params=params)

    def get_user(self, userid):
        """get user"""
        params = {'userid': userid}
        return self._get('cgi-bin/user/get', params=params)

    def upload_media(self, mtype, file_path=None, file_content=None):
        """upload media"""
        suffies = {'image': '.jpg', 'voice': '.mp3', 'video': '.mp4', 'file': ''}
        return super(WxApi, self).upload_media(
            mtype, file_path=file_path, file_content=file_content,
            url='cgi-bin/media/upload', suffies=suffies)

    def download_media(self, media_id, to_path):
        """download media"""
        return super(WxApi, self).download_media(media_id, to_path, 'cgi-bin/media/get')

    def send_message(self, msg_type, content, agentid, safe="0", touser=None,
                     toparty=None, totag=None, **kwargs):
        """send message"""
        func = {'text': self.send_text,
                'image': self.send_image,
                'voice': self.send_voice,
                'video': self.send_video,
                'file': self.send_file,
                'news': self.send_news,
                'mpnews': self.send_mpnews}.get(msg_type, None)
        if func:
            return func(content, agentid, safe=safe, touser=touser,
                        toparty=toparty, totag=totag, **kwargs)
        else:
            return None, None

    def send_text(self, content, agentid, safe="0", touser=None, toparty=None, totag=None):
        """send text"""
        params = {'touser': format_list(touser),
                  'toparty': format_list(toparty),
                  'totag': format_list(totag),
                  'msgtype': 'text',
                  'agentid': agentid,
                  'safe': safe,
                  'text': {'content': content}}
        return self._post('cgi-bin/message/send', simplify_send_parmas(params))

    def send_simple_media(self, mtype, media_id, agentid, safe="0", touser=None, toparty=None,
                          totag=None, media_url=None):
        """send simple media"""
        if media_id and media_id.startswith('http'):
            media_url = media_id
            media_id = None
        mid = self._get_media_id({'media_id': media_id, 'media_url': media_url}, 'media', mtype)
        params = {'touser': format_list(touser),
                  'toparty': format_list(toparty),
                  'totag': format_list(totag),
                  'msgtype': mtype,
                  'agentid': agentid,
                  'safe': safe,
                  mtype: {'media_id': mid}}
        return self._post('cgi-bin/message/send', simplify_send_parmas(params))

    def send_image(self, media_id, agentid, safe="0", touser=None, toparty=None, totag=None,
                   media_url=None):
        """send_image"""
        return self.send_simple_media('image', media_id, agentid, safe, touser, toparty, totag,
                                      media_url)

    def send_voice(self, media_id, agentid, safe="0", touser=None, toparty=None, totag=None,
                   media_url=None):
        """send_voice"""
        return self.send_simple_media('voice', media_id, agentid, safe, touser, toparty, totag,
                                      media_url)

    def send_file(self, media_id, agentid, safe="0", touser=None, toparty=None, totag=None,
                  media_url=None):
        """send_file"""
        return self.send_simple_media('file', media_id, agentid, safe, touser, toparty, totag,
                                      media_url)

    def send_video(self, video, agentid, safe="0", touser=None, toparty=None, totag=None,
                   media_url=None):
        """send_video"""
        video['media_id'] = self._get_media_id(video, 'media', 'video')
        if 'media_url' in video:
            del video['media_url']
        params = {'touser': format_list(touser),
                  'toparty': format_list(toparty),
                  'totag': format_list(totag),
                  'msgtype': 'video',
                  'agentid': agentid,
                  'safe': safe,
                  'video': video}
        return self._post('cgi-bin/message/send', simplify_send_parmas(params))

    def send_news(self, news, agentid, safe="0", touser=None, toparty=None, totag=None,
                  media_url=None):
        """send_news"""
        if isinstance(news, dict):
            news = [news]
        params = {'touser': format_list(touser),
                  'toparty': format_list(toparty),
                  'totag': format_list(totag),
                  'msgtype': 'news',
                  'agentid': agentid,
                  'safe': safe,
                  'news': {'articles': news}}
        return self._post('cgi-bin/message/send', simplify_send_parmas(params))

    def send_mpnews(self, mpnews, agentid, safe="0", touser=None, toparty=None, totag=None,
                    media_url=None):
        """send_mpnews"""
        news = mpnews
        if isinstance(mpnews, dict):
            news = [mpnews]
        params = {'touser': format_list(touser),
                  'toparty': format_list(toparty),
                  'totag': format_list(totag),
                  'msgtype': 'mpnews',
                  'agentid': agentid,
                  'safe': safe,
                  'mpnews': {'articles': news}}
        return self._post('cgi-bin/message/send', simplify_send_parmas(params))

    def create_menu(self, menus, agentid):
        """create_menu"""
        return self._post('cgi-bin/menu/create?agentid=%s' % agentid, repr(menus), ctype='text')

    def get_menu(self, agentid):
        """get_menu"""
        return self._get('cgi-bin/menu/get', {'agentid': agentid})

    def delete_menu(self, agentid):
        """delete_menu"""
        return self._get('cgi-bin/menu/delete', {'agentid': agentid})

    # OAuth2
    def authorize_url(self, appid, redirect_uri, response_type='code',
                      scope='snsapi_base', state=None):
        """authorize url"""
        params = dict(appid=appid, redirect_uri=redirect_uri, response_type=response_type,
                      scope=scope)
        if state:
            params['state'] = state
        url = '?'.join(
            ['https://open.weixin.qq.com/connect/oauth2/authorize',
             urllib.urlencode(sorted(params.items()))])
        url = '#'.join([url, 'wechat_redirect'])
        return url

    def get_user_info(self, agentid, code):
        """get_user_info"""
        return self._get('cgi-bin/user/getuserinfo', {'agentid': agentid, 'code': code})
