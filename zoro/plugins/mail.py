#! /usr/bin/env python
# -*- coding: utf-8 -*-
import logging


def init(all_cfg, plugin_cfg):
    pass


def send(rule, ret, cfg):
    logging.debug("mail send:%s %s", rule, ret)
