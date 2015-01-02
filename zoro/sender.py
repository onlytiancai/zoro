#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
- 有独立的线程定时发送告警, 保证单位时间内不会有太多的告警骚扰到用户
- 被收敛的告警，在时间到了之后会自动合并，一次发送给用户
'''
import logging
import threading
import time
from datetime import datetime, timedelta 
import utils

mutex = threading.Lock()
tobe_send = []
max_queue = 10
sender_plugins = {}
warning_send_thread = None

class WarningSendThread(threading.Thread):
    def __init__(self, cfg):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.setName("warning send thread")
        self.cfg = cfg
        self.min_warning_send_interval = cfg.get("min_warning_send_interval", 60)

    def run(self):
        logging.info("warning send thread runing")
        while True:
            try:
                last_warning_send_at = self.cfg.get('last_warning_send_at', datetime.min)
                logging.debug("warning send thread:%s %s", last_warning_send_at, datetime.now())
                if datetime.now() - last_warning_send_at < timedelta(seconds=self.min_warning_send_interval):
                    continue

                # 复制一份后清空
                mutex.acquire()
                warnings = tobe_send[:]
                tobe_send[:] = []
                mutex.release()

                _send(warnings, self.cfg)
            except:
                logging.exception("warning send thread error")
            finally:
                time.sleep(1)


def init(cfg):
    global warning_send_thread
    warning_send_thread = WarningSendThread(cfg)
    warning_send_thread.start()
    plugins = utils.get_modules(cfg, "senders")
    sender_plugins.update(plugins)


def _send(warnings, cfg):
    if len(warnings) < 1:
        return
    cfg['last_warning_send_at'] = datetime.now()
    for rule, ret in warnings:
        rule['keep_fail_count'] = 0
    for name, sender in sender_plugins.items():
        try:
            logging.info("send warning:%s %s", name, warnings)
            sender.send(warnings, cfg)
        except:
            logging.exception("send warning err:%s %s", name, warnings)


def sendwarnings(rule, ret, cfg):
    last_warning_send_at = cfg.get('last_warning_send_at', datetime.min)
    min_warning_send_interval = cfg.get("min_warning_send_interval", 60)
    logging.info("sendwarnings recive:%s %s", rule, ret)

    if datetime.now() - last_warning_send_at < timedelta(min_warning_send_interval):
        mutex.acquire()
        if len(tobe_send) < max_queue:
            tobe_send.append((rule, ret))
        else:
            logging.info("sendwarnings queue full:%s %s", rule, ret)
        mutex.release()
    else:
        _send([(rule, ret)], cfg)
