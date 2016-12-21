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
        token = eval('self.' + token_type)
        expires = eval('self.' + token_type + '_expires')
        token = None if token == 'None' else token
        expires = time() - 60 if expires == 'None' or expires is None else float(expires)
        if not token and not expires:
            for i in range(3):
                sleep(3)
                if eval('self.' + token_type):
                    break
        elif not token or expires and expires < time():
            exec("self." + token_type + "_expires = None")
            self.__refresh_token(fn_get_token, token_type)
        return eval('self.' + token_type)

    def __refresh_token(self, fn_get_token, token_type):
        """refresh_token"""
        token, err = fn_get_token()
        if token and not err:
            try:
                exec("self." + token_type + " = token['access_token']")
            except KeyError:
                exec("self." + token_type + " = token['ticket']")
            exec("self." + token_type + "_expires = time() + token['expires_in']")
        else:
            exec("self." + token_type + " = None")


class LocalTokenManager(TokenManager):
    """LocalTokenManager"""

    def __init__(self, postfix=""):
        """init"""
        self.postfix = postfix
        self.localdb = {}

        self.__access_token_name = "_".join(['access_token', self.postfix])
        self.__access_token_expires_name = "_".join(['access_token', 'expires', self.postfix])

        self.__jsapi_ticket_name = "_".join(['jsapi_ticket', self.postfix])
        self.__jsapi_ticket_expires_name = "_".join(['jsapi_ticket', 'expires', self.postfix])

        self.__api_ticket_name = "_".join(['api_ticket', self.postfix])
        self.__api_ticket_expires_name = "_".join(['api_ticket', 'expires', self.postfix])

    # access_token
    @property
    def access_token(self):
        """get token"""
        return self.localdb.get(self.__access_token_name)

    @access_token.setter
    def access_token(self, access_token):
        """set token"""
        self.localdb.update({self.__access_token_name: access_token})

    @property
    def access_token_expires(self):
        """get expires"""
        return self.localdb.get(self.__access_token_expires_name)

    @access_token_expires.setter
    def access_token_expires(self, access_token_expires):
        """set expires"""
        self.localdb.update({self.__access_token_expires_name: access_token_expires})

    # jsapi_ticket
    @property
    def jsapi_ticket(self):
        """get jsapi_ticket"""
        return self.localdb.get(self.__jsapi_ticket_name)

    @jsapi_ticket.setter
    def jsapi_ticket(self, jsapi_ticket):
        """set jsapi_ticket"""
        self.localdb.update({self.__jsapi_ticket_name: jsapi_ticket})

    @property
    def jsapi_ticket_expires(self):
        """get jsapi_ticket_expires"""
        return self.localdb.get(self.__jsapi_ticket_expires_name)

    @jsapi_ticket_expires.setter
    def jsapi_ticket_expires(self, jsapi_ticket_expires):
        """set jsapi_ticket_expires"""
        self.localdb.update({self.__jsapi_ticket_expires_name: jsapi_ticket_expires})

    # api_ticket
    @property
    def api_ticket(self):
        """get api_ticket"""
        return self.localdb.get(self.__api_ticket_name)

    @api_ticket.setter
    def api_ticket(self, api_ticket):
        """set api_ticket"""
        self.localdb.update({self.__api_ticket_name: api_ticket})

    @property
    def api_ticket_expires(self):
        """get api_ticket_expires"""
        return self.localdb.get(self.__api_ticket_expires_name)

    @api_ticket_expires.setter
    def api_ticket_expires(self, api_ticket_expires):
        """set api_ticket_expires"""
        self.localdb.update({self.__api_ticket_expires_name: api_ticket_expires})


class RedisTokenManager(TokenManager):
    """RedisTokenManager"""

    def __init__(self, postfix="", **kwargs):
        """init"""
        self.postfix = postfix
        self.redis = redis.Redis(**kwargs)

        self.__access_token_name = "_".join(['access_token', self.postfix])
        self.__access_token_expires_name = "_".join(['access_token', 'expires', self.postfix])

        self.__jsapi_ticket_name = "_".join(['jsapi_ticket', self.postfix])
        self.__jsapi_ticket_expires_name = "_".join(['jsapi_ticket', 'expires', self.postfix])

        self.__api_ticket_name = "_".join(['api_ticket', self.postfix])
        self.__api_ticket_expires_name = "_".join(['api_ticket', 'expires', self.postfix])

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
        return expires.decode() if expires and isinstance(expires, bytes) else expires

    @access_token_expires.setter
    def access_token_expires(self, access_token_expires):
        """set expires"""
        self.redis.set(self.__access_token_expires_name, access_token_expires)

    # jsapi_ticket
    @property
    def jsapi_ticket(self):
        """get jsapi_ticket"""
        token = self.redis.get(self.__jsapi_ticket_name)
        return token.decode() if token and isinstance(token, bytes) else token

    @jsapi_ticket.setter
    def jsapi_ticket(self, jsapi_ticket):
        """set jsapi_ticket"""
        self.redis.set(self.__jsapi_ticket_name, jsapi_ticket)

    @property
    def jsapi_ticket_expires(self):
        """get jsapi_ticket_expires"""
        expires = self.redis.get(self.__jsapi_ticket_expires_name)
        return expires.decode() if expires and isinstance(expires, bytes) else expires

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
        return expires.decode() if expires and isinstance(expires, bytes) else expires

    @api_ticket_expires.setter
    def api_ticket_expires(self, api_ticket_expires):
        """set api_ticket_expires"""
        self.redis.set(self.__api_ticket_expires_name, api_ticket_expires)
