# -*- coding: utf-8 -*-
import psutil
import re
import logging
from collections import namedtuple

RuleConfig = namedtuple('RuleConfig', ['patt', 'title'])

class Rule(object):
    'Rule插件类，必须使用Rule作为类名'
     
    def __init__(self, options):
        '插件初始化方法，options是插件配置数据'
        self.options = options
        self._load_rules()

    def _load_rules(self):
        self.rules = []
        for k, v in self.options.items():
            if not k.startswith('rule'):
                continue
            last_space_index = v.rindex(' ')
            cmd_patten = v[:last_space_index].strip()
            title = v[last_space_index + 1:]
            
            rule = RuleConfig(cmd_patten, title)
            logging.info('load rule config:%s', rule)
            self.rules.append(rule)

    def _isrun(self, process_list, patt):
        for p in process_list:
            cmdline = ' '.join(p.cmdline)
            if re.search(patt, cmdline):
                return True
        return False

    def process(self, data, historys):
        '''插件方法，必须实现
        data是最新的计数数据，caches是最近的数据'''
        process_list = psutil.get_process_list()
        for rule in self.rules:
            if not self._isrun(process_list, rule.patt):
                return self._get_send_data(rule)

        return None

    def _get_send_data(self, rule):
        result = {}
        result['title'] = rule.title
        result['content'] = '没有检测到进程在运行：%s' % rule.patt
        result['host'] = self.options['host'] if 'host' in self.options else 'default'
        return result
