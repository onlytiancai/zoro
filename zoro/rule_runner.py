#! /usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import time
import multiprocessing

def run(rule, cfg, module):
    args = rule.get("args", {})
    logging.debug("plugin %s runing:%s", rule["type"], args)
    try:
        module.do(**args)
    except:
        logging.exception("plugin %s run error:%s", rule["type"], args)
    time.sleep(60)


def runall(rules, cfg, plugins):
    run_interval = cfg.get("run_interval", 60)
    run_timeout = cfg.get("run_timeout", 5)
    logging.debug("runall:%s", run_interval)
    while True:
        try:
            ps = []
            for rule in rules:
                p = multiprocessing.Process(target=run, args=(rule, cfg, plugins[rule['type']]))
                p.daemon = True
                ps.append(p)

            for p in ps:
                p.start()
            
            begin_time = time.time()
            for p in ps:
                timeout = abs(run_timeout - (time.time() - begin_time))
                logging.debug('process join:%s', timeout)
                p.join(timeout)
                if p.is_alive():
                    p.terminate()
                    p.join()
        finally:
            time.sleep(run_interval)
