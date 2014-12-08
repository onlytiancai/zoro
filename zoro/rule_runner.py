#! /usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import time
import multiprocessing


def run(rule, cfg, module, queue):
    args = rule.get("args", {})
    logging.debug("plugin %s runing:%s", rule["type"], args)
    try:
        ret = module.do(**args)
        queue.put(ret)
    except:
        logging.exception("plugin %s run error:%s", rule["type"], args)


def runall(rules, cfg, plugins):
    run_interval = cfg.get("run_interval", 60)
    run_timeout = cfg.get("run_timeout", 5)
    logging.debug("runall:%s", run_interval)
    while True:
        try:
            ps = [] # p, q, rule
            for rule in rules:
                q = multiprocessing.Queue() # 取子进程结果
                p = multiprocessing.Process(target=run, args=(rule, cfg, plugins[rule['type']], q))
                p.daemon = True
                ps.append((p, q, rule))

            for p, q, rule in ps:
                p.start()
            
            begin_time = time.time()
            for p, q, rule in ps:
                timeout = abs(run_timeout - (time.time() - begin_time))
                logging.debug('process join:%s', timeout)
                p.join(timeout)
                if p.is_alive():
                    p.terminate()
                    p.join()

                if not q.empty():
                    logging.info('process result:%s %s(%s)', q.get(), rule['type'], rule['id'])
                else:
                    logging.warn('process result is empty:%s(%s)', rule['type'], rule['id'])
        finally:
            time.sleep(run_interval)
