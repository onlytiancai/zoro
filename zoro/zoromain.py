#! /usr/bin/env python
# -*- coding: utf-8 -*-
import daemon
import time
import logging

import config
import utils

utils.init_logger(config.log_dir, config.log_level, config.log_console)
logging.debug("zoro start")

with daemon.DaemonContext():
    while True:
        time.sleep(1)
