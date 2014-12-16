#! /usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import time
import multiprocessing

import utils
import sender

rule_plugins = {}

def init(cfg):
    plugins = utils.get_modules(cfg, "rules")
    rule_plugins.update(plugins)


def task_success(rule, cfg):
    success_count = rule.get('success_count', 0)
    rule['success_count'] = success_count + 1
    rule['keep_fail_count'] = 0
    logging.debug('task_success:%s', rule)


def task_fail(rule, ret, cfg):
    fail_count = rule.get('fail_count', 0)
    rule['fail_count'] = fail_count + 1

    max_keep_fail_count = rule.get('max_keep_fail_count', cfg.get('max_keep_fail_count', 3))
    keep_fail_count = rule.get('keep_fail_count', 0)
    rule['keep_fail_count'] = keep_fail_count + 1
    if keep_fail_count >= max_keep_fail_count:
        sender.sendwarnings(rule, ret)
    logging.debug('task_fail:%s', rule)


def run(rule, cfg, module, queue):
    args = rule.get("args", {})
    logging.debug("plugin %s runing:%s", rule["type"], args)
    try:
        ret = module.do(**args)
        queue.put(ret)
    except:
        logging.exception("plugin %s run error:%s", rule["type"], args)


def runall(cfg):
    rules = cfg.get('rules', [])
    run_interval = cfg.get("run_interval", 60)
    run_timeout = cfg.get("run_timeout", 5)
    logging.debug("runall:%s", run_interval)
    while True:
        try:
            ps = []  # p, q, rule
            for rule in rules:
                q = multiprocessing.Queue()  # 取子进程结果
                p = multiprocessing.Process(target=run, args=(rule, cfg, rule_plugins[rule['type']], q))
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

                if not q.empty():  # 任务执行成功, 得到结果
                    ret = q.get()
                    logging.info('process result:%s %s(%s)', ret, rule['type'], rule['id'])
                    if ret:  # 任务返回数据表示监控异常
                        task_fail(rule, ret, cfg)
                    else:
                        task_success(rule, cfg)
                else:  # 任务执行失败，未得到结果，可能是执行超时被kill
                    logging.warn('process result is empty:%s(%s)', rule['type'], rule['id'])
                    task_fail(rule, "execute timeout", cfg)
        finally:
            time.sleep(run_interval)
