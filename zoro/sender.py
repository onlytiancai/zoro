j! /usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import threading
import Queue
import time
from datetime import datetime, timedelta 
import utils

sender_plugins = {}
tobe_send = Queue.Queue(20) # 满了就算了
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
                last_warning_send_at = cfg.get('last_warning_send_at', datetime.min)
                if datetime.now() - last_warning_send_at < timedelta(self.min_warning_send_interval):
                    continue
                cfg['last_warning_send_at'] = datetime.now()
                warnings = []
                while not tobe_send.empty():
                    warning = tobe_send.get()
                    warnings.append(warning)
                    tobe_send.task_done() 

                cfg['last_warning_send_at'] = datetime.now()
                sendwarnings(warnings, self.cfg)
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


def _send(warnings, cfg)
    for rule, ret in warnings:
        rule['keep_fail_count'] = 0
    for name, sender in sender_plugins.items():
        try:
            logging.debug("send warning:%s %s", name, warnings)
            sender.send(warnings, cfg)
        except:
            logging.exception("send warning err:%s %s", name, warnings)


def sendwarnings(rule, ret):
    tobe_send.put((rule, ret))
