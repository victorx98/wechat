# -*- coding: utf-8 -*-
"""token manager"""
from time import time, sleep
import logging
import redis

logger = logging.getLogger(__name__)


class TokenManager(object):
    """TokenManager"""

    # def get_token(self, fn_get_token, token_type):
    #     """get_token"""
    #     if token_type == 'access_token':
    #         __token =
    #     if token_type == 'jsapi_ticket':
    #         pass
    #     if token_type == 'api_ticket':
    #         pass
    #
    # def __refresh_token(self, fn_get_token, token_type):
    #     """refresh_token"""
    #     if token_type == 'access_token':
    #         pass
    #     if token_type == 'jsapi_ticket':
    #         pass
    #     if token_type == 'api_ticket':
    #         pass


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

        # self.__token = None
        # self.__expires = None

        self.__access_token_name = "_".join(['access_token', self.postfix])
        self.__access_token_expires_name = "_".join(['access_token', 'expires', self.postfix])

        self.__jsapi_ticket_name = "_".join(['jsapi_ticket', self.postfix])
        self.__jsapi_ticket_atk_name = "_".join(['jsapi_ticket', 'atk', self.postfix])
        self.__jsapi_ticket_expires_name = "_".join(['jsapi_ticket', 'expires', self.postfix])

        self.__api_ticket_name = "_".join(['api_ticket', self.postfix])
        self.__api_ticket_atk_name = "_".join(['api_ticket', 'atk', self.postfix])
        self.__api_ticket_expires_name = "_".join(['api_ticket', 'expires', self.postfix])

        # if not self.expires:
        #     self.expires = time()

    def get_token(self, fn_get_token, token_type):
        """get_token"""

        token, expires, atk = self._read_token('access_token')
        expires = time() - 60 if expires is None else expires
        if not token or float(expires) < time():
            self.__refresh_token(fn_get_token, 'access_token')
            token, expires, atk = self._read_token('access_token')
        print('0-access_token:', token)

        if not token_type == 'access_token':
            print('01-当前token_type:', token_type)
            ticket, expires, atk = self._read_token('access_token')
            expires = time() - 60 if expires is None else expires
            print('01-atk:', atk)
            print('01-curr_token[', token_type, ']:', token)
            print('01-时间过期:', float(expires) < time())
            print('01-token对比不等:', not (token == atk))
            if not ticket or not (token == atk) or float(expires) < time():
                print('01-2-刷新:token')
                self.__refresh_token(fn_get_token, token_type, token)
                ticket, _, _ = self._read_token(token_type)
            token = ticket
        return token

    def __refresh_token(self, fn_get_token, token_type, curr_token=None):
        """refresh_token"""
        if token_type == 'access_token':
            token, err = fn_get_token()
            print('3-原始token:', token)
            if token and not err:
                _token = token['access_token']
                _expires = time() + token['expires_in']
                self._write_token(_token, _expires, token_type)
            else:
                self._write_token(None, None, token_type)
        if token_type == 'jsapi_ticket':
            curr_token = self.get_token(fn_get_token, 'access_token')
            print('3-curr_token:', curr_token)
            if curr_token is not None:
                token, err = fn_get_token(access_token=curr_token)
                print('3-原始jspai_ticket:', token)
                print('3-传入的curr_token:', curr_token)
                if token and not err:
                    _token = token['ticket']
                    _atk = curr_token
                    _expires = time() + token['expires_in']
                    self._write_token(_token, _expires, token_type, _atk)
                else:
                    self._write_token(None, None, token_type)

        if token_type == 'api_ticket':
            # curr_token = self.get_token(fn_get_token, 'access_token')
            print('3-curr_token:', curr_token)
            if curr_token is not None:
                token, err = fn_get_token(access_token=curr_token)
                print('3-原始api_ticket:', token)
                if token and not err:
                    _token = token['ticket']
                    _atk = curr_token
                    _expires = time() + token['expires_in']
                    self._write_token(_token, _expires, token_type, _atk)
                else:
                    self._write_token(None, None, token_type)

    def _read_token(self, token_type):
        token, expires, atk = ('None', time(), None)
        if token_type == 'access_token':
            token = self.redis.get(self.__access_token_name)
            token = token.decode() if token and isinstance(token, bytes) else token
            expires = self.redis.get(self.__access_token_expires_name)
            expires = expires.decode() if expires and isinstance(expires, bytes) else expires
        if token_type == 'jsapi_ticket':
            token = self.redis.get(self.__jsapi_ticket_name)
            token = token.decode() if token and isinstance(token, bytes) else token
            atk = self.redis.get(self.__jsapi_ticket_atk_name)
            atk = atk.decode() if atk and isinstance(atk, bytes) else atk
            expires = self.redis.get(self.__jsapi_ticket_expires_name)
            expires = expires.decode() if expires and isinstance(expires, bytes) else expires
        if token_type == 'api_ticket':
            token = self.redis.get(self.__api_ticket_name)
            token = token.decode() if token and isinstance(token, bytes) else token
            atk = self.redis.get(self.__api_ticket_atk_name)
            atk = atk.decode() if atk and isinstance(atk, bytes) else atk
            expires = self.redis.get(self.__api_ticket_expires_name)
            expires = expires.decode() if expires and isinstance(expires, bytes) else expires
        token = None if token == 'None' else token
        atk = None if atk == 'None' else atk
        expires = time() if expires == 'None' else expires
        return token, expires, atk

    def _write_token(self, token_value, token_expires, token_type, token_atk=None):
        if token_type == 'access_token':
            self.redis.set(self.__access_token_name, token_value)
            self.redis.set(self.__access_token_expires_name, token_expires)
        if token_type == 'jsapi_ticket':
            self.redis.set(self.__jsapi_ticket_name, token_value)
            self.redis.set(self.__jsapi_ticket_atk_name, token_atk)
            self.redis.set(self.__jsapi_ticket_expires_name, token_expires)
        if token_type == 'api_ticket':
            self.redis.set(self.__api_ticket_name, token_value)
            self.redis.set(self.__api_ticket_atk_name, token_atk)
            self.redis.set(self.__api_ticket_expires_name, token_expires)

            # @property
            # def token(self):
            #     return self.__token
            #
            # @token.setter
            # def token(self, token):
            #     self.__token = token
            #
            # @property
            # def expires(self):
            #     return self.__expires
            #
            # @expires.setter
            # def expires(self, expires):
            #     self.__expires = expires

            # # access_token
            # @property
            # def access_token(self):
            #     """get token"""
            #     token = self.redis.get(self.__access_token_name)
            #     return token.decode() if token and isinstance(token, bytes) else token
            #
            # @access_token.setter
            # def access_token(self, access_token):
            #     """set token"""
            #     self.redis.set(self.__access_token_name, access_token)
            #
            # @property
            # def access_token_expires(self):
            #     """get expires"""
            #     expires = self.redis.get(self.__access_token_expires_name)
            #     return expires.decode() if expires and isinstance(expires, bytes) else expires
            #
            # @access_token_expires.setter
            # def access_token_expires(self, access_token_expires):
            #     """set expires"""
            #     self.redis.set(self.__access_token_expires_name, access_token_expires)
            #
            # # jsapi_ticket
            # @property
            # def jsapi_ticket(self):
            #     """get jsapi_ticket"""
            #     token = self.redis.get(self.__jsapi_ticket_name)
            #     return token.decode() if token and isinstance(token, bytes) else token
            #
            # @jsapi_ticket.setter
            # def jsapi_ticket(self, jsapi_ticket):
            #     """set jsapi_ticket"""
            #     self.redis.set(self.__jsapi_ticket_name, jsapi_ticket)
            #
            # @property
            # def jsapi_ticket_expires(self):
            #     """get jsapi_ticket_expires"""
            #     expires = self.redis.get(self.__jsapi_ticket_expires_name)
            #     return expires.decode() if expires and isinstance(expires, bytes) else expires
            #
            # @jsapi_ticket_expires.setter
            # def jsapi_ticket_expires(self, jsapi_ticket_expires):
            #     """set jsapi_ticket_expires"""
            #     self.redis.set(self.__jsapi_ticket_expires_name, jsapi_ticket_expires)
            #
            # # api_ticket
            # @property
            # def api_ticket(self):
            #     """get api_ticket"""
            #     token = self.redis.get(self.__api_ticket_name)
            #     return token.decode() if token and isinstance(token, bytes) else token
            #
            # @api_ticket.setter
            # def api_ticket(self, api_ticket):
            #     """set api_ticket"""
            #     self.redis.set(self.__api_ticket_name, api_ticket)
            #
            # @property
            # def api_ticket_expires(self):
            #     """get api_ticket_expires"""
            #     expires = self.redis.get(self.__api_ticket_expires_name)
            #     return expires.decode() if expires and isinstance(expires, bytes) else expires
            #
            # @api_ticket_expires.setter
            # def api_ticket_expires(self, api_ticket_expires):
            #     """set api_ticket_expires"""
            #     self.redis.set(self.__api_ticket_expires_name, api_ticket_expires)
