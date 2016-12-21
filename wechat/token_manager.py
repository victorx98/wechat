# -*- coding: utf-8 -*-
"""token manager"""
from time import time, sleep
import logging
import redis

logger = logging.getLogger(__name__)


class TokenManager(object):
    """TokenManager"""

    def get_token(self, fn_get_token, token_type):
        """get_token"""
        # token = {
        #     'access_token': self.access_token,
        #     'jsapi_ticket': self.jsapi_ticket,
        #     'api_ticket': self.api_ticket
        # }.get(token_type)
        # expires = {
        #     'access_token': self.access_token_expires,
        #     'jsapi_ticket': self.jsapi_ticket_expires,
        #     'api_ticket': self.api_ticket_expires,
        # }.get(token_type)
        token = eval('self.' + token_type)
        expires = eval('self.' + token_type + '_expires')
        print('token:', token)
        print('expires:', expires)

        # if not token and not expires:
        #     for i in range(12):
        #         sleep(5)
        #         print('self.token***:', eval('self.'+token_type))
        #         if eval('self.'+token_type):
        #             break
        # elif not token or expires and float(expires) < time():
        if not token or expires and float(expires) < time():
            exec("self." + token_type + "_expires = None")
            self.__refresh_token(fn_get_token, token_type)
        if token is None:
            token = eval('self.' + token_type)
        print('get返回的token:', token)
        return token

    def __refresh_token(self, fn_get_token, token_type):
        """refresh_token"""
        # token, err = fn_get_token()
        # if token and not err:
        #     print('原始token:', token)
        #     if token_type == 'access_token':
        #         self.access_token = token['access_token']
        #         self.access_token_expires = time() + token['expires_in']
        #     if token_type == 'jsapi_ticket':
        #         self.jsapi_ticket = token['ticket']
        #         self.jsapi_ticket_expires = time() + token['expires_in']
        #     if token_type == 'api_ticket':
        #         self.api_ticket = token['ticket']
        #         self.api_ticket_expires = time() + token['expires_in']
        # else:
        #     if token_type == 'access_token':
        #         self.access_token = None
        #     if token_type == 'jsapi_ticket':
        #         self.jsapi_ticket = None
        #     if token_type == 'api_ticket':
        #         self.api_ticket = None
        token, err = fn_get_token()
        if token and not err:
            print('原始token:', token)
            try:
                exec("self." + token_type + " = token['access_token']")
            except KeyError:
                exec("self." + token_type + " = token['ticket']")
            exec("self." + token_type + "_expires = time() + token['expires_in']")
        else:
            exec("self." + token_type + " = None")


class LocalTokenManager(TokenManager):
    """LocalTokenManager"""

    def __init__(self, postfix="", **kwargs):
        """init"""
        self.postfix = postfix
        self.redis = redis.Redis(**kwargs)
        self.__curr_token = None
        self.__curr_expires = None

        self.__access_token_name = "_".join(['access_token', self.postfix])
        self.__access_token_expires_name = "_".join(['access_token', 'expires', self.postfix])

        self.__jsapi_ticket_name = "_".join(['jsapi_ticket', self.postfix])
        self.__jsapi_ticket_expires_name = "_".join(['jsapi_ticket', 'expires', self.postfix])

        self.__api_ticket_name = "_".join(['api_ticket', self.postfix])
        self.__api_ticket_expires_name = "_".join(['api_ticket', 'expires', self.postfix])

        if not self.access_token_expires:
            self.access_token_expires = time()
        if not self.jsapi_ticket_expires:
            self.jsapi_ticket_expires = time()
        if not self.api_ticket_expires:
            self.api_ticket_expires = time()

    @property
    def token(self):
        """get token"""
        return self.__curr_token

    @token.setter
    def token(self, token):
        """set token"""
        self.__curr_token = token

    @property
    def expires(self):
        """get expires"""
        return self.__curr_expires

    @expires.setter
    def expires(self, expires):
        """set expires"""
        self.__curr_expires = expires

    # access_token
    @property
    def access_token(self):
        """get token"""
        token = self.redis.get(self.__access_token_name)
        return token.decode() if token and isinstance(token, bytes) else token

    @access_token.setter
    def access_token(self, access_token):
        """set token"""
        self.redis.set(self.__access_token_name, access_token)

    @property
    def access_token_expires(self):
        """get expires"""
        expires = self.redis.get(self.__access_token_expires_name)
        return expires

    @access_token_expires.setter
    def access_token_expires(self, access_token_expires):
        """set expires"""
        self.redis.set(self.__access_token_expires_name, access_token_expires)

    # jsapi_ticket
    @property
    def jsapi_ticket(self):
        """get jsapi_ticket"""
        token = self.redis.get(self.__jsapi_ticket_name)
        print('获取jsapi_ticket:', token)
        return token.decode() if token and isinstance(token, bytes) else token

    @jsapi_ticket.setter
    def jsapi_ticket(self, jsapi_ticket):
        """set jsapi_ticket"""
        print('设置jsapi_ticket:', jsapi_ticket)
        self.redis.set(self.__jsapi_ticket_name, jsapi_ticket)

    @property
    def jsapi_ticket_expires(self):
        """get jsapi_ticket_expires"""
        expires = self.redis.get(self.__jsapi_ticket_expires_name)
        return expires

    @jsapi_ticket_expires.setter
    def jsapi_ticket_expires(self, jsapi_ticket_expires):
        """set jsapi_ticket_expires"""
        self.redis.set(self.__jsapi_ticket_expires_name, jsapi_ticket_expires)

    # api_ticket
    @property
    def api_ticket(self):
        """get api_ticket"""
        token = self.redis.get(self.__api_ticket_name)
        return token.decode() if token and isinstance(token, bytes) else token

    @api_ticket.setter
    def api_ticket(self, api_ticket):
        """set api_ticket"""
        self.redis.set(self.__api_ticket_name, api_ticket)

    @property
    def api_ticket_expires(self):
        """get api_ticket_expires"""
        expires = self.redis.get(self.__api_ticket_expires_name)
        return expires

    @api_ticket_expires.setter
    def api_ticket_expires(self, api_ticket_expires):
        """set api_ticket_expires"""
        self.redis.set(self.__api_ticket_expires_name, api_ticket_expires)


class RedisTokenManager(object):
    """RedisTokenManager"""

    def __init__(self, postfix="", *args, **kwargs):
        """init"""
        self.postfix = postfix
        self._token_type = None
        self.token_name = None
        self.expires_name = None
        self.redis = redis.Redis(*args, **kwargs)
        if not self.expires:
            self.expires = time()

    @property
    def token(self):
        """get token"""
        if self._token_type is not None:
            self.token_name = "_".join([self._token_type, self.postfix])
            token = self.redis.get(self.token_name)
            token = str(token, "utf-8") if token and isinstance(
                token, bytes) else token
            print({self._token_type: token})
            return {self._token_type: token}
        else:
            print('_token_type:None')
            return None

    @token.setter
    def token(self, token):
        """set token"""
        if self._token_type is not None:
            self.token_name = "_".join([self._token_type, self.postfix])
            self.redis.set(self.token_name, token)

    @property
    def expires(self):
        """get expires"""
        if self._token_type is not None:
            self.expires_name = "_".join([self._token_type, "expires", self.postfix])
            expires = self.redis.get(self.expires_name)
            return {self._token_type: expires}
        else:
            print('get expires--> _token_type:None')
            return None

    @expires.setter
    def expires(self, expires):
        """set expires"""
        if self._token_type is not None:
            self.expires_name = "_".join([self._token_type, "expires", self.postfix])
            self.redis.set(self.expires_name, expires)

    def get_token(self, fn_get_access_token, token_type=None):
        """get_token"""
        if isinstance(self.token, dict):
            token = self.token.get(token_type)
        else:
            token = self.token
        if isinstance(self.expires, dict):
            expires = self.expires.get(token_type, time())
        else:
            expires = time()

        if not token and not expires:
            for i in range(12):
                sleep(5)
                if self.token:
                    break
        elif not token or expires and float(expires) < time():
            self.expires = None
            self.refresh_token(fn_get_access_token, token_type)
        return self.token.get(token_type)

    def refresh_token(self, fn_get_access_token, token_type):
        """refresh_token"""
        token, err = fn_get_access_token()
        if token and not err:
            print(token_type)
            print('原始token:', token)
            self._token_type = token_type
            if token_type == 'access_token':
                key_name = 'access_token'
            else:
                key_name = 'ticket'
            self.token = token[key_name]
            self.expires = time() + token['expires_in']
        else:
            self.token = None
            self._token_type = None
