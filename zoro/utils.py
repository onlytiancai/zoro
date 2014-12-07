#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os
import logging
import logging.handlers

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
