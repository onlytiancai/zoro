#! /usr/bin/env python
# -*- coding: utf-8 -*-
# import daemon
import time
import logging

import config
import utils
import sender
import rule_runner

utils.init_logger(config.log_dir, config.log_level, config.log_console)
logging.info("zoro start")

utils.init_for_setup()

zorocfg = utils.load_user_config(config.user_config_path)
sender.init(zorocfg)
rule_runner.init(zorocfg)
rule_runner.runall(zorocfg)

time.sleep(10000)

# TODO
# with daemon.DaemonContext():
#     while True:
#         time.sleep(1)
