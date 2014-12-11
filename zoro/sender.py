#! /usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import utils

sender_plugins = {}

def init(cfg):
    plugins = utils.get_modules(cfg, "senders")
    sender_plugins.update(plugins)

def send(rule, ret, cfg):
    rule['keep_fail_count'] = 0
    for name, sender in sender_plugins.items():
        try:
            logging.debug("send warning:%s %s %s", name, rule, ret)
            sender.send(rule, ret, cfg)
        except:
            logging.exception("send warning err:%s %s %s", name, rule, ret)
