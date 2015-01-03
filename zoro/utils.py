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
    logging.info("init_for_setup %s %s", config.user_config_path, config.user_plugins_path)
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
    formatter = logging.Formatter('%(asctime)s %(levelname)s (%(module)s)[%(process)d] - %(message)s')
    handler.setFormatter(formatter)
    if console:
        consoleHandler = logging.StreamHandler()
        consoleHandler.setFormatter(formatter)
        logger.addHandler(consoleHandler)
    logger.addHandler(handler)


def load_user_config(config_path):
    lines = open(config_path).read().splitlines()

    # 过滤掉json配置里的注释
    json_str = ''
    for line in lines:
        line = line.strip()
        if line.startswith('#'):
            continue
        json_str += line

    cfg = json.loads(json_str)
    logging.info("load_user_config: %s", json.dumps(cfg, indent=4))
    return cfg


def run_rules(cfg):
    plugins = {}
    rules = cfg.get('rules', [])

    for i, rule in enumerate(rules):
        rule['id'] = i + 1
        module_name = rule["type"]
        if module_name in plugins:
            continue

        f, filename, desc = imp.find_module(module_name, [config.plugins_path, config.user_plugins_path])
        module = imp.load_module(module_name, f, filename, desc)
        plugins[module_name] = module
        logging.info("load plugins:%s %s", module_name, filename)

        if hasattr(module, "init"):
            module.init(cfg)

    rule_runner.runall(rules, cfg, plugins)

def get_modules(all_cfg, plugin_cfgs_name):
    ret = {}
    plugin_cfgs = all_cfg.get(plugin_cfgs_name, [])

    for i, plugin_cfg in enumerate(plugin_cfgs):
        plugin_cfg['id'] = i + 1
        plugin_name = plugin_cfg["type"]
        if plugin_name in ret:
            continue

        f, filename, desc = imp.find_module(plugin_name, [config.plugins_path, config.user_plugins_path])
        module = imp.load_module(plugin_name, f, filename, desc)
        ret[plugin_name] = module
        logging.info("load plugins:%s %s", plugin_name, filename)

        if hasattr(module, "init"):
            module.init(all_cfg, plugin_cfg)

    return ret
