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
APP_ID = os.environ.get('WX_APP_ID', 'wxc6a2d04030e04a94')
APP_SECRET = os.environ.get('WX_APP_SECRET', 'fd91aea8d2b7082ccf01dd0d6b0e1752')
TOKEN = os.environ.get('WX_TOKEN', '884CD2D9')
ENCODING_AES_KEY = os.environ.get('WX_AES_KEY', None)
UNSUPPORT_TXT = '暂不支持此类型消息'
WELCOME_TXT = '欢迎重新回来！\n' \
              '我是测试圈公认懂的最多的人，人称『百晓生』。我这里每天提供一篇原创测试好文。' \
              '你每天还能问我一个问题，你觉得会难住我吗？把我装进口袋，总会有用处的 : )'
