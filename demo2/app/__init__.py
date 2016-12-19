#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Youngson
# @Email: Youngson.gu@gmail.com
# @Date:   2016-12-19 10:11
# @Last Modified by:   Administrator
# @Last Modified time: 2016-12-19 10:11
from flask import Flask
from demo2.app import config

APP = Flask(__name__)
APP.config.from_object(config)
from demo2.app import views
