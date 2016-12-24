# -*- coding: utf-8 -*-
"""official"""
from functools import wraps
import json
import tempfile
import shutil
import os
import sys
from datetime import datetime, timedelta
import requests
from .crypt import WXBizMsgCrypt, SHA1

from .models import WxRequest, WxResponse
from .models import WxMusic, WxArticle, WxImage, WxVoice, WxVideo, WxLink
from .models import WxTextResponse, WxImageResponse, WxVoiceResponse, \
    WxVideoResponse, WxMusicResponse, WxNewsResponse, APIError, WxEmptyResponse

__all__ = ['WxRequest', 'WxResponse', 'WxMusic', 'WxArticle', 'WxImage',
           'WxVoice', 'WxVideo', 'WxLink', 'WxTextResponse',
           'WxImageResponse', 'WxVoiceResponse', 'WxVideoResponse',
           'WxMusicResponse', 'WxNewsResponse', 'WxApplication',
           'WxEmptyResponse', 'WxApi', 'APIError']


class WxApplication(object):
    """WxApplication"""
    UNSUPPORT_TXT = u'暂不支持此类型消息'
    WELCOME_TXT = u'你好！感谢您的关注！'
    SECRET_TOKEN = None
    APP_ID = None
    ENCODING_AES_KEY = None

    def __init__(self):
        """init"""
        # 外部继承是可扩展,此处自定义的handle
        self.handlers = None
        self.event_handlers = {
            'subscribe': self.on_subscribe,
            'unsubscribe': self.on_unsubscribe,
            'SCAN': self.on_scan,
            'LOCATION': self.on_location_update,
            'CLICK': self.on_click,
            'VIEW': self.on_view,
            'scancode_push': self.on_scancode_push,
            'scancode_waitmsg': self.on_scancode_waitmsg,
            'pic_sysphoto': self.on_pic_sysphoto,
            'pic_photo_or_album': self.on_pic_photo_or_album,
            'pic_weixin': self.on_pic_weixin,
            'location_select': self.on_location_select
        }

    def is_valid_params(self, params):
        """valid params"""
        timestamp = params.get('timestamp', '')
        nonce = params.get('nonce', '')
        signature = params.get('signature', '')
        echostr = params.get('echostr', '')

        if (signature == SHA1.get_signature(self.token, timestamp, nonce)):
            return True, echostr
        else:
            return None

    def process(self, params, xml=None, token=None, app_id=None, aes_key=None):
        """process"""
        self.token = token if token else self.SECRET_TOKEN
        self.app_id = app_id if app_id else self.APP_ID
        self.aes_key = aes_key if aes_key else self.ENCODING_AES_KEY
        self.cpt = None
        self.nonce = None

        assert self.token is not None

        ret = self.is_valid_params(params)

        if not ret:
            return 'invalid request'
        if not xml:
            # 微信开发者设置的调用测试
            return ret[1]

        # 解密消息
        encrypt_type = params.get('encrypt_type', '')
        if encrypt_type != '' and encrypt_type != 'raw':
            msg_signature = params.get('msg_signature', '')
            timestamp = params.get('timestamp', '')
            self.nonce = params.get('nonce', '')
            if encrypt_type == 'aes':
                self.cpt = WXBizMsgCrypt(self.token, self.aes_key, self.app_id)
                err, xml = self.cpt.decrypt_msg(xml, msg_signature, timestamp, self.nonce)
                if err:
                    return 'decrypt message error, code : %s' % err
            else:
                return 'unsupport encrypty type %s' % encrypt_type

        req = WxRequest(xml)
        self.wxreq = req
        func = self.handler_map().get(req.MsgType, None)
        if not func:
            return WxTextResponse(self.UNSUPPORT_TXT, req)
        self.pre_process()
        rsp = func(req)
        self.post_process(rsp)
        result = rsp.as_xml().encode('UTF-8')

        # 加密消息
        if encrypt_type != '' and encrypt_type != 'raw':
            if encrypt_type == 'aes':
                err, result = self.cpt.encrypt_msg(result, self.nonce)
                if err:
                    return 'encrypt message error , code %s' % err
            else:
                return 'unsupport encrypty type %s' % encrypt_type
        return result

    def on_text(self, text):
        """text"""
        return WxTextResponse(self.UNSUPPORT_TXT, text)

    def on_link(self, link):
        """link"""
        return WxTextResponse(self.UNSUPPORT_TXT, link)

    def on_image(self, image):
        """image"""
        return WxTextResponse(self.UNSUPPORT_TXT, image)

    def on_voice(self, voice):
        """voice"""
        return WxTextResponse(self.UNSUPPORT_TXT, voice)

    def on_video(self, video):
        """video"""
        return WxTextResponse(self.UNSUPPORT_TXT, video)

    def on_location(self, loc):
        """location"""
        return WxTextResponse(self.UNSUPPORT_TXT, loc)

    def on_event(self, event):
        """event"""
        func = self.event_handlers.get(event.Event, self.on_other_event)
        return func(event)

    def on_other_event(self, event):
        """other_event"""
        # Unhandled event
        return WxEmptyResponse()

    def on_subscribe(self, sub):
        """subscribe"""
        return WxTextResponse(self.WELCOME_TXT, sub)

    def on_unsubscribe(self, unsub):
        """unsubscribe"""
        return WxEmptyResponse()

    def on_click(self, click):
        """click"""
        return WxEmptyResponse()

    def on_scan(self, scan):
        """scan"""
        return WxEmptyResponse()

    def on_location_update(self, location):
        """location_update"""
        return WxEmptyResponse()

    def on_view(self, view):
        """"""
        return WxEmptyResponse()

    def on_scancode_push(self, event):
        """scancode_push"""
        return WxEmptyResponse()

    def on_scancode_waitmsg(self, event):
        """scancode_waitmsg"""
        return WxEmptyResponse()

    def on_pic_sysphoto(self, event):
        """pic_sysphoto"""
        return WxEmptyResponse()

    def on_pic_photo_or_album(self, event):
        """pic_photo_or_album"""
        return WxEmptyResponse()

    def on_pic_weixin(self, event):
        """pic_weixin"""
        return WxEmptyResponse()

    def on_location_select(self, event):
        """location_select"""
        return WxEmptyResponse()

    def handler_map(self):
        """handler map"""
        if getattr(self, 'handlers', None):
            return self.handlers
        return {
            'text': self.on_text,
            'link': self.on_link,
            'image': self.on_image,
            'voice': self.on_voice,
            'video': self.on_video,
            'location': self.on_location,
            'event': self.on_event,
        }

    def pre_process(self):
        """pre_process"""
        pass

    def post_process(self, rsp=None):
        """post_process"""
        pass


def retry_token(fn):
    """retry_token"""

    def wrapper(self, *args, **kwargs):
        """装饰器"""
        content, err = fn(self, *args, **kwargs)
        if not content and err and err.code in [40001, 40014, 42001]:
            self.token_manager.refresh_token(self.get_access_token)
            return fn(self, *args, **kwargs)
        else:
            return content, err

    return wrapper


class WxBaseApi(object):
    """WxBaseApi"""
    API_PREFIX = 'https://api.weixin.qq.com/cgi-bin/'
    VERIFY = True

    def __init__(self, appid, appsecret, token_manager, api_entry=None):
        """init"""
        self.appid = appid
        self.appsecret = appsecret
        self.token_manager = token_manager
        self.api_entry = api_entry or self.API_PREFIX

    @property
    def access_token(self):
        return self.token_manager.get_token(self.get_access_token)

    @property
    def jsapi_ticket(self):
        return self.get_jsapi_ticket()

    @property
    def api_ticket(self):
        return self.get_api_ticket()

    def _process_response(self, rsp):
        """process response"""
        if rsp.status_code != 200:
            return None, APIError(rsp.status_code, 'http error')
        try:
            content = rsp.json()
        except Exception:
            return None, APIError(99999, 'invalid rsp')
        if 'errcode' in content and content['errcode'] != 0:
            return None, APIError(content['errcode'], content['errmsg'])
        return content, None

    @retry_token
    def _get(self, path, params=None):
        """_get"""
        if not params:
            params = {}
        params['access_token'] = self.access_token
        rsp = requests.get(self.api_entry + path, params=params,
                           verify=WxBaseApi.VERIFY)
        print(rsp.url)
        return self._process_response(rsp)

    @retry_token
    def _post(self, path, data, ctype='json'):
        """_post"""
        headers = {'Content-type': 'application/json'}
        path = self.api_entry + path
        if '?' in path:
            path += '&access_token=' + self.access_token
        else:
            path += '?access_token=' + self.access_token
        if ctype == 'json':
            data = json.dumps(data, ensure_ascii=False).encode('utf-8')
        rsp = requests.post(path, data=data, headers=headers,
                            verify=WxBaseApi.VERIFY)
        return self._process_response(rsp)

    def upload_media(self, mtype, file_path=None, file_content=None, url='media/upload',
                     suffies=None):
        """upload_media"""
        path = self.api_entry + url + '?access_token=' \
               + self.access_token + '&type=' + mtype
        suffies = suffies or {'image': '.jpg', 'voice': '.mp3', 'video': 'mp4', 'thumb': 'jpg'}
        suffix = None
        tmp_path = None
        if mtype in suffies:
            suffix = suffies[mtype]
        if file_path:
            fd, tmp_path = tempfile.mkstemp(suffix=suffix)
            shutil.copy(file_path, tmp_path)
            os.close(fd)
        elif file_content:
            fd, tmp_path = tempfile.mkstemp(suffix=suffix)
            f = os.fdopen(fd, 'wb')
            f.write(file_content)
            f.close()
        media = open(tmp_path, 'rb')
        rsp = requests.post(path, files={'media': media},
                            verify=WxBaseApi.VERIFY)
        media.close()
        os.remove(tmp_path)
        return self._process_response(rsp)

    def download_media(self, media_id, to_path, url='media/get'):
        """download_media"""
        rsp = requests.get(self.api_entry + url,
                           params={'media_id': media_id,
                                   'access_token': self.access_token},
                           verify=WxBaseApi.VERIFY)
        if rsp.status_code == 200:
            save_file = open(to_path, 'wb')
            save_file.write(rsp.content)
            save_file.close()
            return {'errcode': 0}, None
        else:
            return None, APIError(rsp.status_code, 'http error')

    def _get_media_id(self, obj, resource, content_type):
        """_get_media_id"""
        if not obj.get(resource + '_id'):
            rsp, err = None, None
            if obj.get(resource + '_content'):
                rsp, err = self.upload_media(
                    content_type,
                    file_content=obj.get(resource + '_content'))
                if err:
                    return None
            elif obj.get(resource + '_url'):
                req = requests.get(obj.get(resource + '_url'))
                rsp, err = self.upload_media(
                    content_type,
                    file_content=req.content)
                if err:
                    return None
            else:
                return None
            return rsp['media_id']
        return obj.get(resource + '_id')


class WxApi(WxBaseApi):
    """WxApi"""

    def get_access_token(self, url=None, **kwargs):
        params = {'grant_type': 'client_credential', 'appid': self.appid,
                  'secret': self.appsecret}
        if kwargs:
            params.update(kwargs)
        rsp = requests.get(url or self.api_entry + 'token', params=params,
                           verify=WxBaseApi.VERIFY)
        return self._process_response(rsp)

    @retry_token
    def get_jsapi_ticket(self):
        """get_jsapi_ticket"""
        params = {'access_token': self.access_token, 'type': 'jsapi'}
        print('params:', params)
        rsp = requests.get('https://api.weixin.qq.com/cgi-bin/ticket/getticket', params=params,
                           verify=WxBaseApi.VERIFY)
        print(rsp.url)
        print('原始rsp:', rsp.text)
        return self._process_response(rsp)

    @retry_token
    def get_api_ticket(self):
        """get_api_ticket"""
        params = {'access_token': self.access_token, 'type': 'wx_card'}
        print('params:', params)
        rsp = requests.get('https://api.weixin.qq.com/cgi-bin/ticket/getticket', params=params,
                           verify=WxBaseApi.VERIFY)
        print(rsp.url)
        print('原始rsp:', rsp.text)
        return self._process_response(rsp)

    def user_info(self, user_id, lang='zh_CN'):
        """user_info"""
        return self._get('user/info', {'openid': user_id, 'lang': lang})

    def followers(self, next_id=''):
        """followers"""
        return self._get('user/get', {'next_openid': next_id})

    def send_message(self, to_user, msg_type, content):
        """send_message"""
        func = {'text': self.send_text,
                'image': self.send_image,
                'voice': self.send_voice,
                'video': self.send_video,
                'music': self.send_music,
                'news': self.send_news}.get(msg_type, None)
        if func:
            return func(to_user, content)
        return None, None

    def send_text(self, to_user, content):
        """send_text"""
        return self._post('message/custom/send',
                          {'touser': to_user, 'msgtype': 'text',
                           'text': {'content': content}})

    def send_image(self, to_user, media_id=None, media_url=None):
        """send_image"""
        if media_id and media_id.startswith('http'):
            media_url = media_id
            media_id = None
        mid = self._get_media_id(
            {'media_id': media_id, 'media_url': media_url},
            'media', 'image')
        return self._post('message/custom/send',
                          {'touser': to_user, 'msgtype': 'image',
                           'image': {'media_id': mid}})

    def send_voice(self, to_user, media_id=None, media_url=None):
        """send_voice"""
        if media_id and media_id.startswith('http'):
            media_url = media_id
            media_id = None
        mid = self._get_media_id(
            {'media_id': media_id, 'media_url': media_url},
            'media', 'voice')
        return self._post('message/custom/send',
                          {'touser': to_user, 'msgtype': 'voice',
                           'voice': {'media_id': mid}})

    def send_music(self, to_user, music):
        """send_music"""
        music['thumb_media_id'] = self._get_media_id(music,
                                                     'thumb_media',
                                                     'image')
        if not music.get('thumb_media_id'):
            return None, APIError(41006, 'missing media_id')
        return self._post('message/custom/send',
                          {'touser': to_user, 'msgtype': 'music',
                           'music': music})

    def send_video(self, to_user, video):
        """send_video"""
        video['media_id'] = self._get_media_id(video, 'media', 'video')
        video['thumb_media_id'] = self._get_media_id(video,
                                                     'thumb_media', 'image')
        if 'media_id' not in video or 'thumb_media_id' not in video:
            return None, APIError(41006, 'missing media_id')
        return self._post('message/custom/send',
                          {'touser': to_user, 'msgtype': 'video',
                           'video': video})

    def send_news(self, to_user, news):
        """send_news"""
        if isinstance(news, dict):
            news = [news]
        return self._post('message/custom/send',
                          {'touser': to_user, 'msgtype': 'news',
                           'news': {'articles': news}})

    def send_template(self, to_user, template_id, url, data):
        """send_template"""
        return self._post('message/template/send',
                          {'touser': to_user, 'template_id': template_id,
                           'url': url, 'data': data})

    def create_group(self, name):
        """create_group"""
        return self._post('groups/create',
                          {'group': {'name': name}})

    def groups(self):
        """groups"""
        return self._get('groups/get')

    def update_group(self, group_id, name):
        """update_group"""
        return self._post('groups/update',
                          {'group': {'id': group_id, 'name': name}})

    def group_of_user(self, user_id):
        """group_of_user"""
        return self._get('groups/getid', {'openid': user_id})

    def move_user_to_group(self, user_id, group_id):
        """move_user_to_group"""
        return self._post('groups/members/update',
                          {'openid': user_id, 'to_groupid': group_id})

    def create_menu(self, menus):
        """create_menu"""
        return self._post('menu/create', menus)

    def get_menu(self):
        """get_menu"""
        return self._get('menu/get')

    def delete_menu(self):
        """delete_menu"""
        return self._get('menu/delete')

    def create_tag(self, name):
        """create_tag"""
        return self._post('tags/create',
                          {'tag': {"name": name}})

    def tags(self):
        """tags"""
        return self._get('tags/get')

    def update_tag(self, tag_id, name):
        """update_tag"""
        return self._post('tags/update',
                          {'tag': {'id': tag_id, 'name': name}})

    def delete_tag(self, tag_id):
        """delete_tag"""
        return self._post('tags/delete',
                          {'tag': {'id': tag_id}})

    def tag_of_user(self, user_id):
        """tag_of_user"""
        return self._post('tags/getidlist', {'openid': user_id})

    def batch_tagging(self, tag_id, users_list):
        """batch_tagging"""
        return self._post('tags/members/batchtagging',
                          {'openid_list': users_list, 'tagid': tag_id})

    def batch_untagging(self, tag_id, users_list):
        """batch_untagging"""
        return self._post('tags/members/batchuntagging',
                          {'openid_list': users_list, 'tagid': tag_id})

    def get_blacklist(self, user_id=""):
        """get_blacklist"""
        return self._post('tags/members/getblacklist',
                          {'begin_openid': user_id})

    def batch_blacklist(self, users_list):
        """batch_blacklist"""
        return self._post('tags/members/batchblacklist',
                          {'openid_list': users_list})

    def batch_unblacklist(self, users_list):
        """batch_unblacklist"""
        return self._post('tags/members/batchunblacklist',
                          {'openid_list': users_list})

    def update_user_remark(self, openid, remark):
        """update_user_remark"""
        return self._post('user/info/updateremark',
                          {'openid': openid, 'remark': remark})

    def customservice_records(self, starttime, endtime, openid=None, pagesize=100, pageindex=1):
        """customservice_records"""
        return self._get('customservice/getrecord',
                         {'starttime': starttime,
                          'endtime': endtime,
                          'openid': openid,
                          'pagesize': pagesize,
                          'pageindex': pageindex})
