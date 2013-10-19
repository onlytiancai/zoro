# -*- coding: utf-8 -*-
import urllib
import urllib2

class StatHat:

        def http_post(self, path, data):
                pdata = urllib.urlencode(data)
                req = urllib2.Request('http://api.stathat.com' + path, pdata)
                resp = urllib2.urlopen(req)
                return resp.read()

        def post_value(self, user_key, stat_key, value, timestamp=None):
                args = {'key': stat_key, 'ukey': user_key, 'value': value}
                if timestamp is not None:
                        args['t'] = timestamp
                return self.http_post('/v', args)

        def post_count(self, user_key, stat_key, count, timestamp=None):
                args = {'key': stat_key, 'ukey': user_key, 'count': count}
                if timestamp is not None:
                        args['t'] = timestamp
                return self.http_post('/c', args)

        def ez_post_value(self, ezkey, stat_name, value, timestamp=None):
                args = {'ezkey': ezkey, 'stat': stat_name, 'value': value}
                if timestamp is not None:
                        args['t'] = timestamp
                return self.http_post('/ez', args)

        def ez_post_count(self, ezkey, stat_name, count, timestamp=None):
                args = {'ezkey': ezkey, 'stat': stat_name, 'count': count}
                if timestamp is not None:
                        args['t'] = timestamp
                return self.http_post('/ez', args)

from datetime import datetime


class Logger(object):
    'Logger插件类，必须使用Logger作为类名'

    log_caches = []

    def __init__(self, options):
        '插件初始化方法，options是插件配置数据'
        self.max_log_cache = int(options['max_log_cache'])
        self.username = options['stathat_username'].strip()
        self.stathat = StatHat()
        
    def log(self, counter_data):
        '插件方法，保存日志数据'
        for k, v in counter_data.items():
            self.stathat.ez_post_value(self.username, k, int(v))


        if len(self.log_caches) >= self.max_log_cache:
            self.log_caches.pop(0)

        counter_data['time'] = datetime.now()
        self.log_caches.append(counter_data)

    def get_last_historys(self):
        '所有logger必须实现，返回最近几条计数器日志，用于在报警判断逻辑中使用'
        return self.log_caches
