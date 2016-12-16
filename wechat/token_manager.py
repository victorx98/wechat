# -*- coding: utf-8 -*-
"""token manager"""
from time import time, sleep
import logging
import redis

logger = logging.getLogger(__name__)


class TokenManager(object):
    """TokenManager"""

    def get_token(self, fn_get_access_token):
        """get_token"""
        token = self.token
        expires = self.expires
        if not token and not expires:
            for i in range(12):
                sleep(5)
                if self.token:
                    break
        elif not token or expires and float(expires) < time():
            self.expires = None
            self.refresh_token(fn_get_access_token)
        return self.token

    def refresh_token(self, fn_get_access_token):
        """refresh_token"""
        token, err = fn_get_access_token()
        if token and not err:
            self.token = token['access_token']
            self.expires = time() + token['expires_in']
        else:
            self.token = None


class LocalTokenManager(TokenManager):
    """LocalTokenManager"""

    def __init__(self):
        self._access_token = None
        self._expires = time()

    @property
    def token(self):
        """get token"""
        return self._access_token

    @token.setter
    def token(self, token):
        """set token"""
        self._access_token = token

    @property
    def expires(self):
        """get expires"""
        return self._expires

    @expires.setter
    def expires(self, expires):
        """set expires"""
        self._expires = expires


class RedisTokenManager(TokenManager):
    """RedisTokenManager"""

    def __init__(self, postfix="", *args, **kwargs):
        """init"""
        self.token_name = "_".join(["access_token", postfix])
        self.expires_name = "_".join(["access_token_expires", postfix])
        self.redis = redis.Redis(*args, **kwargs)
        if not self.expires:
            self.expires = time()

    @property
    def token(self):
        """get token"""
        token = self.redis.get(self.token_name)
        return str(token, "utf-8") if token and isinstance(
            token, bytes) else token

    @token.setter
    def token(self, token):
        """set token"""
        self.redis.set(self.token_name, token)

    @property
    def expires(self):
        """get expires"""
        expires = self.redis.get(self.expires_name)
        return expires

    @expires.setter
    def expires(self, expires):
        """set expires"""
        self.redis.set(self.expires_name, expires)
