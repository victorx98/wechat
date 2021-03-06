# -*- coding: utf-8 -*-
"""component for wechat"""
import json
from hashlib import sha1

import requests
import xmltodict

from .crypt import WXBizMsgCrypt
from .models import APIError


class WxComponentApplication(object):
    """Component"""
    SECRET_TOKEN = None
    APP_ID = None
    ENCODING_AES_KEY = None

    def __init__(self):
        """init"""
        # 外部继承是可扩展,此处自定义的handle
        self.handlers = None

    def is_valid_params(self, params):
        """valid params"""
        timestamp = params.get('timestamp', '')
        nonce = params.get('nonce', '')
        signature = params.get('signature', '')
        echostr = params.get('echostr', '')

        sign_ele = [self.token, timestamp, nonce]
        sign_ele.sort()
        if signature == sha1(''.join(sign_ele)).hexdigest():
            return True, echostr
        else:
            return None

    def process(self, params, xml=None, token=None, app_id=None, aes_key=None):
        """Process"""
        self.token = token if token else self.SECRET_TOKEN
        self.app_id = app_id if app_id else self.APP_ID
        self.aes_key = aes_key if aes_key else self.ENCODING_AES_KEY
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
            nonce = params.get('nonce', '')
            if encrypt_type == 'aes':
                cpt = WXBizMsgCrypt(self.token, self.aes_key, self.app_id)
                err, xml = cpt.decrypt_msg(xml, msg_signature, timestamp, nonce)
                if err:
                    return 'decrypt message error, code : %s' % err
            else:
                return 'unsupport encrypty type %s' % encrypt_type

        event = xmltodict.parse(xml)['xml']
        info_type = event.get('InfoType')

        func = self.handler_map().get(info_type, None)
        if not func:
            return "success"
        func(event)
        return "success"

    def handler_map(self):
        """handler map"""
        if getattr(self, 'handlers', None):
            return self.handlers
        return {
            'component_verify_ticket': self.on_verify_ticket,
            'unauthorized': self.on_unauthorized,
            'authorized': self.on_authorized,
            'updateauthorized': self.on_updateauthorized,
        }

    def on_verify_ticket(self, event):
        """
        字段名称	                  字段描述
        AppId	                  第三方平台appid
        CreateTime	              时间戳
        InfoType	              component_verify_ticket
        ComponentVerifyTicket	  Ticket内容
        """
        pass

    def on_unauthorized(self, event):
        """
        字段名称	                        字段描述
        AppId	                        第三方平台appid
        CreateTime	                    时间戳
        InfoType	                    unauthorized是取消授权
        AuthorizerAppid	                公众号
        AuthorizationCode	            授权码，可用于换取公众号的接口调用凭据
        AuthorizationCodeExpiredTime	授权码过期时间
        """
        pass

    def on_authorized(self, event):
        """
        字段名称	                        字段描述
        AppId	                        第三方平台appid
        CreateTime	                    时间戳
        InfoType	                    authorized是授权成功
        AuthorizerAppid	                公众号
        AuthorizationCode	            授权码，可用于换取公众号的接口调用凭据
        AuthorizationCodeExpiredTime	授权码过期时间
        """
        pass

    def on_updateauthorized(self, event):
        """
        字段名称	                        字段描述
        AppId	                        第三方平台appid
        CreateTime	                    时间戳
        InfoType	                    updateauthorized是更新授权
        AuthorizerAppid	                公众号
        AuthorizationCode	            授权码，可用于换取公众号的接口调用凭据
        AuthorizationCodeExpiredTime	授权码过期时间
        """
        pass


class WxComponentApi(object):
    """
    微信公众号第三方平台API
    """

    COMPONENT_APP_ID = None
    COMPONENT_APP_SECRET = None

    API_PREFIX = 'https://api.weixin.qq.com/cgi-bin/'

    def __init__(self, component_appid=None, component_appsecret=None, api_entry=None):
        """
        由于这是公众号第三方平台的API,
        """
        self.component_appid = component_appid or self.COMPONENT_APP_ID
        self.component_appsecret = component_appsecret or self.COMPONENT_APP_SECRET
        self.api_entry = api_entry or self.API_PREFIX

    def _process_response(self, rsp):
        """process response"""
        if rsp.status_code != 200:
            return None, APIError(rsp.status_code, 'http error')
        try:
            content = rsp.json()
        except:
            return None, APIError(99999, 'invalid rsp')
        if 'errcode' in content and content['errcode'] != 0:
            return None, APIError(content['errcode'], content['errmsg'])
        return content, None

    def _post(self, path, data, ctype='json'):
        """post"""
        headers = {'Content-type': 'application/json'}
        path = self.api_entry + path
        if ctype == 'json':
            data = json.dumps(data, ensure_ascii=False).encode('utf-8')
        rsp = requests.post(path, data=data, headers=headers, verify=False)
        return self._process_response(rsp)

    def get_component_access_token(self, verify_ticket):
        """
        获取第三方平台component_access_token
        """
        parameters = {
            "component_appid": self.component_appid,
            "component_appsecret": self.component_appsecret,
            'component_verify_ticket': verify_ticket
        }
        rsp = self._post("component/api_component_token", parameters)
        return rsp

    def get_pre_auth_code(self, component_access_token):
        """
        获取预授权码
        """
        pre_auth_code_url = "component/api_create_preauthcode?component_access_token=" \
                            "%s" % component_access_token
        parameters = {
            'component_appid': self.component_appid
        }
        rsp = self._post(pre_auth_code_url, parameters)
        return rsp

    def get_authorization_page(self, pre_auth_code, redirect_uri):
        """
        获取第三方平台授权页地址
        """
        authorization_page = "https://mp.weixin.qq.com/cgi-bin/componentloginpage?component_appid=" \
                             "%s&pre_auth_code=%s&redirect_uri=%s" % (
                                 self.component_appid, pre_auth_code, redirect_uri)
        return authorization_page

    def get_authorization_info(self, auth_code, component_access_token):
        """
        获取授权公众号的授权信息
        """
        url = "component/api_query_auth?component_access_token=%s" % component_access_token
        parameters = {
            "component_appid": self.component_appid,
            "authorization_code": auth_code
        }
        rsp = self._post(url, parameters)
        return rsp
