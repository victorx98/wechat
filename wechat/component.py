# coding=utf-8

import xmltodict
from hashlib import sha1
from .crypt import WXBizMsgCrypt


class WxComponentApplication(object):

    SECRET_TOKEN = None
    APP_ID = None
    ENCODING_AES_KEY = None

    def is_valid_params(self, params):
        timestamp = params.get('timestamp', '')
        nonce = params.get('nonce', '')
        signature = params.get('signature', '')
        echostr = params.get('echostr', '')

        sign_ele = [self.token, timestamp, nonce]
        sign_ele.sort()
        if(signature == sha1(''.join(sign_ele)).hexdigest()):
            return True, echostr
        else:
            return None

    def process(self, params, xml=None, token=None, app_id=None, aes_key=None):
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
                err, xml = cpt.DecryptMsg(xml, msg_signature, timestamp, nonce)
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