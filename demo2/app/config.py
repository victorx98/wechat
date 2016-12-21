#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Youngson
# @Email: Youngson.gu@gmail.com
# @Date:   2016-12-19 10:28
# @Last Modified by:   Administrator
# @Last Modified time: 2016-12-19 10:28

import os

DEBUG = True

HOST_NAME = 'localhost'
APP_NAME = 'Wechat Demo'
HOST_IP = '127.0.0.1'
HOST_PORT = 80

# Wechat
APP_ID = os.environ.get('WX_APP_ID', '')
APP_SECRET = os.environ.get('WX_APP_SECRET', '')
TOKEN = os.environ.get('WX_TOKEN', '')
ENCODING_AES_KEY = os.environ.get('WX_AES_KEY', None)
UNSUPPORT_TXT = '暂不支持此类型消息'
WELCOME_TXT = '欢迎重新回来！\n'
# Redis
REDIS_HOST = os.environ.get('REDIS_HOST', '127.0.0.1')
REDIS_PORT = os.environ.get('REDIS_PORT', 6379)
REDIS_DB = os.environ.get('REDIS_DB', 0)
