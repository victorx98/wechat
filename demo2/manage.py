#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Youngson
# @Email: Youngson.gu@gmail.com
# @Date:   2016-12-19 10:10
# @Last Modified by:   Administrator
# @Last Modified time: 2016-12-19 10:10

from demo2.app import APP
from demo2.app.config import HOST_IP, HOST_PORT, DEBUG

if __name__ == '__main__':
    APP.run(HOST_IP, HOST_PORT, DEBUG)
