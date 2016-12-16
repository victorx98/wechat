#!/usr/bin/env python
'''App setup config'''
from setuptools import setup, find_packages
from wechat import VERSION

URL = "https://github.com/jeffkit/wechat"

LONG_DESCRIPTION = "Wechat Python SDK"

setup(name="wechat",
      version=VERSION,
      description=LONG_DESCRIPTION,
      maintainer="jeff kit",
      maintainer_email="bbmyth@gmail.com",
      url=URL,
      long_description=LONG_DESCRIPTION,
      install_requires=['requests'],
      packages=find_packages('.'), )
