#! /usr/bin/env python
# -*- coding: utf-8 -*-
import urllib
import logging

def do(target):
    "返回None表示成功，否则返回错误信息"
    logging.debug("plugin curl do:%s", target)
    urllib.urlopen(target)
    return "curl error"  # TODO For test


def init(all_cfg, plugin_cfg):
    "可选的插件初始化方法，会传入整个用户配置"
    logging.debug("plugin curl init")
