#! /usr/bin/env python
# -*- coding: utf-8 -*-
import daemon
import logging
import time

pid = "/tmp/test.pid"
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.propagate = False
fh = logging.FileHandler("/tmp/test.log", "w")
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)


logger.debug("Test")

with daemon.DaemonContext():
    while True:
        time.sleep(1)
