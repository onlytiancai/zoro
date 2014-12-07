#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os

log_dir = '/data/logs/zoro'
log_level = 'DEBUG'
log_console = True 

plugins_path = './plugins/'

user_home_path = os.getenv("HOME")
user_plugins_path = os.path.join(user_home_path, '.zoro/plugins/')
user_config_path = os.path.join(user_home_path, '.zoro/config.json')

