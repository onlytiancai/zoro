#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os
import logging
import logging.handlers
import json
import imp
import shutil

import config 
import rule_runner 

def init_for_setup():
    logging.debug("init_for_setup %s %s", config.user_config_path, config.user_plugins_path)
    if not os.path.exists(config.user_plugins_path):
        os.makedirs(config.user_plugins_path)

    if not os.path.exists(config.user_config_path):
        shutil.copy('./etc/config.json', config.user_config_path)

    # TODO
    shutil.copy('./etc/config.json', config.user_config_path)

def init_logger(log_dir, level='info', console=False):
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    log_file = os.path.join(log_dir, "all.log")

    logger = logging.getLogger()
    logger.propagate = False
    level = logging._levelNames.get(level.upper(), logging.INFO)
    logger.setLevel(level)
    handler = logging.handlers.RotatingFileHandler(log_file, maxBytes=100 * 1000 * 1000, backupCount=10)
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    handler.setFormatter(formatter)
    if console:
        consoleHandler = logging.StreamHandler()
        consoleHandler.setFormatter(formatter)
        logger.addHandler(consoleHandler)
    logger.addHandler(handler)


def load_user_config(config_path):
    cfg = json.loads(open(config_path).read())
    logging.debug("load_user_config: %s", json.dumps(cfg, indent=4))
    return cfg


def run_rules(cfg):
    plugins = {}
    rules = cfg.get('rules', [])
    for rule in rules:
        module_name = rule["type"]
        if module_name in plugins:
            continue

        f, filename, desc = imp.find_module(module_name, [config.plugins_path, config.user_plugins_path])
        module = imp.load_module(module_name, f, filename, desc)
        plugins[module_name] = module
        logging.info("load plugins:%s %s", module_name, filename)

        if hasattr(module, "init"):
            module.init(cfg)

    for rule in rules:
        rule_runner.run(rule, cfg, plugins[rule['type']])
