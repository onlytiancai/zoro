#! /usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import time
import threading

class Runner(threading.Thread):
    def __init__(self, rule, cfg, module):
        threading.Thread.__init__(self, name="plug:" + rule["type"])
        self.setDaemon(True)
        self.rule = rule
        self.cfg = cfg
        self.module = module
     
    def run(self):
        run_interval = self.rule.get("run_interval", self.cfg.get("run_interval", 60))
        args = self.rule.get("args", {})
        logging.exception("plugin %s runing:%s %s", self.rule["type"], run_interval, args)
        while True:
            try:
                self.module.do(**args)
            except:
                logging.exception("plugin %s run error:%s", self.rule["type"], args)
            finally:
                time.sleep(run_interval)
   

def run(rule, cfg, module):
    runner = Runner(rule, cfg, module)
    runner.start()
