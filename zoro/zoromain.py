#! /usr/bin/env python
# -*- coding: utf-8 -*-
import daemon
import time
import logging

import config
import utils

utils.init_logger(config.log_dir, config.log_level, config.log_console)
logging.debug("zoro start")

utils.init_for_setup()

zorocfg = utils.load_user_config(config.user_config_path)
utils.run_rules(zorocfg)

#with daemon.DaemonContext():
#    while True:
#        time.sleep(1)
