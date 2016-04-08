# -*- coding: utf8 -*-

import ConfigParser
import Queue
import threading
import subprocess
import urllib
import urllib2
import socket
import datetime
import logging
import logging.handlers
import pickle
import os
import commands
import time
import sys

cf = ConfigParser.ConfigParser()
cf.optionxform = str
cf.read('config.ini')


def logger(name, console=False):
    logpath = cf.get('common', name)
    if not os.path.exists(os.path.dirname(logpath)):
        os.makedirs(os.path.dirname(logpath))

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')

    h = logging.handlers.TimedRotatingFileHandler(logpath, 'H', 1, 10)
    h.setFormatter(formatter)
    logger.addHandler(h)

    if console:
        h = logging.StreamHandler()
        h.setFormatter(formatter)
        logger.addHandler(h)

    return logger


statlog = logger('statlog')
debuglog = logger('debuglog', True)
monitors = []
senders = []

DBPATH = './zoro.db'
if cf.has_option('common', 'dbpath'):
    DBPATH = cf.get('common', 'dbpath')

TASK_TIMEOUT = 5
if cf.has_option('common', 'task_timeout'):
    TASK_TIMEOUT = cf.get('common', 'task_timeout')

try:
    import sender
    senders.append(sender.Sender())
    debuglog.info('load ext sender ok')
except ImportError:
    pass
except: 
    debuglog.exception('load ext sender err')


def uuid():
    return commands.getstatusoutput('uuidgen')


def json_dumps(obj):
    try:
        import json
        return json.dumps(obj, indent=4)
    except:
        return obj #TODO, for py 2.4


class MonitorResult(object):
    def __init__(self, succ=True, log='', error=''):
        self.succ = succ
        self.log = log
        self.error = error

    def __str__(self):
        status = 'succ'
        if not self.succ:
            status = 'failed'
        return '%s log=%s error=%s' % (status, self.log, self.error)


class DiskMonitor(object):
    def __init__(self, section):
        self.section = section
        self.max = cf.getint(section, 'max')

    def __str__(self):
        return 'monitor: type=disk, max=%s' % (self.max)

    def run(self):
        output = subprocess.Popen(['/bin/df', '-h'],
                                  stdout=subprocess.PIPE).communicate()[0]

        '''
        Filesystem      Size  Used Avail Use% Mounted on
        /dev/vda1        20G  2.3G   17G  13% /
        '''
        lines = output.splitlines()[1:]
        for line in lines:
            arr = line.split()
            diskuse = int(arr[4].replace('%', ''))
            if diskuse > self.max:
                error = "%s diskuse > %s%%: %s%%" % (arr[0], self.max, diskuse)
                return MonitorResult(False, error=error)

        return MonitorResult(True, log=output)


class LoadMonitor(object):
    def __init__(self, section):
        self.section = section
        self.max = cf.getfloat(section, 'max')

    def __str__(self):
        return 'monitor: type=load, max=%s' % (self.max)

    def run(self):
        output = subprocess.Popen(['/usr/bin/uptime'],
                                  stdout=subprocess.PIPE).communicate()[0]
        '''
         12:29:31 up 6 days, 15:42,  1 user,  load average: 0.00, 0.00, 0.00
        '''
        lines = output.splitlines()
        load5 = lines[0].split(',')[4].strip()
        load5 = float(load5)
        if load5 > self.max:
            error = "load5 > %s: %s" % (self.max, load5)
            return MonitorResult(False, error=error)

        return MonitorResult(True, log=output)


class HttpMonitor(object):
    def __init__(self, section):
        self.section = section
        self.url = cf.get(section, 'url')
        self.timeout = 5
        if cf.has_option(section, 'timeout'):
            self.timeout = cf.getfloat(section, 'timeout')

    def __str__(self):
        return 'monitor: type=http, timeout=%s' % (self.timeout)

    def run(self):
        try:
            version = sys.version_info
            if version[0] == 2 and version[1] == 4:
                rsp = urllib2.urlopen(self.url)
            else:
                rsp = urllib2.urlopen(self.url, timeout=self.timeout)

            rsp = rsp.read()[:100]
            return MonitorResult(True, log=rsp)
        except Exception, ex:
            error = "http task:%s error:%s" % (self.url, ex)
            return MonitorResult(False, error=error)


class ProcessMonitor(object):
    def __init__(self, section):
        self.section = section

        self.keyword = ''
        if cf.has_option(section, 'keyword'):
            self.keyword = cf.get(section, 'keyword').strip("'").strip('"')

        self.min = 1
        if cf.has_option(section, 'min'):
            self.min = cf.getint(section, 'min')

        self.max = cf.getint(section, 'max')

    def __str__(self):
        return 'monitor: type=process, keyword=%s, min=%s, max=%s' \
               % (self.keyword, self.min, self.max)

    def run(self):
        'ps -ef | grep nginx | grep -v grep | wc -l'

        cmd = ['/bin/ps', '-ef']
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE)

        cmd = ['/bin/grep', self.keyword]
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stdin=p.stdout)

        cmd = ['/bin/grep', '-v', 'grep']
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stdin=p.stdout)

        cmd = ['/usr/bin/wc', '-l']
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stdin=p.stdout)
        wc = int(p.communicate()[0])

        log = 'process(%s) count = %s' % (self.keyword, wc)

        if wc > self.max:
            return MonitorResult(False, error=log)

        if wc < self.min:
            return MonitorResult(False, error=log)

        return MonitorResult(True, log=log)


class TcpMonitor(object):
    def __init__(self, section):
        self.section = section
        self.ip = cf.get(section, 'ip')
        self.port = cf.getint(section, 'port')
        self.timeout = 5
        if cf.has_option(section, 'timeout'):
            self.timeout = cf.getfloat(section, 'timeout')

    def __str__(self):
        return 'monitor: type=tcp, ip=%s, port=%s, timeout=%s' \
            % (self.ip, self.port, self.timeout)

    def run(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(self.timeout)
            s.connect((self.ip, self.port))
            s.settimeout(None)
        except Exception, ex:
            error = "tcp addr %s:%s connect error:%s" \
                    % (self.ip, self.port, ex)
            return MonitorResult(False, error=error)

        log = "tcp addr %s:%s connected" % (self.ip, self.port)
        return MonitorResult(True, log=log)


class LogMonitor(object):
    def __init__(self, section):
        self.section = section
        self.logpath = cf.get(section, 'logpath')
        if cf.has_option(section, 'filetimeformat'):
            filetimeformat = cf.get(section, 'filetimeformat')
            filetime = datetime.datetime.now().strftime(filetimeformat)
            self.logpath = self.logpath.replace('{time}', filetime)

        self.timeformat = cf.get(section, 'timeformat')
        self.max = cf.getint(section, 'max')
        self.keyword = cf.get(section, 'keyword').strip("'").strip('"')

    def __str__(self):
        return 'monitor: type=log, logpath=%s, timeformat=%s, max=%s' \
                % (self.logpath, self.timeformat, self.max)

    def run(self):
        logtime = datetime.datetime.now().strftime(self.timeformat)

        cmd = ['/usr/bin/tail', '-n', '100000', self.logpath]
        tail = subprocess.Popen(cmd, stdout=subprocess.PIPE)

        cmd = ['/bin/grep', logtime]
        grep = subprocess.Popen(cmd, stdout=subprocess.PIPE, stdin=tail.stdout)

        cmd = ['/bin/grep', '-E', self.keyword]
        grep = subprocess.Popen(cmd, stdout=subprocess.PIPE, stdin=grep.stdout)

        cmd = ['/usr/bin/wc', '-l']
        wc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stdin=grep.stdout)
        wc = int(wc.communicate()[0])

        log = '`tail -n 100000 "%s" | grep "%s" | grep "%s" | wc -l` = %s ' \
            % (self.logpath, logtime, self.keyword, wc)
        if wc > self.max:
            return MonitorResult(False, error=log)

        return MonitorResult(True, log=log)


class UrlSender(object):
    def __init__(self, section):
        self.url = cf.get(section, 'url')

        self.timeout = 5
        if cf.has_option(section, 'timeout'):
            self.timeout = cf.getfloat(section, 'timeout')

        self.datatype = 'json'
        if cf.has_option(section, 'datatype'):
            self.datatype = cf.get(section, 'datatype')

        if self.datatype == 'json':
            self.headers = {'Content-type': 'application/json'}
        else:
            self.headers = {'Content-type':
                            'application/x-www-form-urlencoded'}

        data = {}
        items = cf.items(section)
        for item in items:
            if item[0].startswith('data-'):
                data[item[0][5:]] = item[1]

        self.data = data

    def send(self, title, content):
        eventid = str(uuid())
        debuglog.info('urlsender title: %s %s', eventid, title)
        debuglog.debug('urlsender content:\n%s', content)

        url = self.url
        url = url.replace('{{title}}', title)
        url = url.replace('{{content}}', content)
        url = url.replace('{{eventid}}', eventid)

        data = {}
        for k, v in self.data.iteritems():
            v = v.replace('{{title}}', title)
            v = v.replace('{{content}}', content)
            v = v.replace('{{eventid}}', eventid)
            data[k] = v

        if self.datatype != 'json':
            postdata = {}
            for k, v in data.iteritems():
                postdata[k] = unicode(v).encode('utf-8')
            postdata = urllib.urlencode(postdata)
        else:
            postdata = json_dumps(data, indent=4)

        try:
            req = urllib2.Request(url, data=postdata,
                                  headers=self.headers)

            version = sys.version_info
            if version[0] == 2 and version[1] == 4:
                rsp = urllib2.urlopen(self.url)
            else:
                rsp = urllib2.urlopen(self.url, timeout=self.timeout)

            rsp = rsp.read()[:100]
            debuglog.info('urlsend ok: %s %s', self.url, rsp)
        except Exception, ex:
            debuglog.error('urlsend error: %s %s', self.url, ex)


class MailSender(object):
    def __init__(self, section):
        pass

    def send(self, title, content):
        pass


for section in cf.sections():
    if section.startswith('monitor'):
        type = cf.get(section, 'type')
        if type == 'disk':
            monitors.append(DiskMonitor(section))
        elif type == 'load':
            monitors.append(LoadMonitor(section))
        elif type == 'http':
            monitors.append(HttpMonitor(section))
        elif type == 'tcp':
            monitors.append(TcpMonitor(section))
        elif type == 'log':
            monitors.append(LogMonitor(section))
        elif type == 'process':
            monitors.append(ProcessMonitor(section))
        else:
            raise Exception('Unknow section: %s' % section)
    elif section.startswith('sender'):
        type = cf.get(section, 'type')
        if type == 'url':
            senders.append(UrlSender(section))
        elif type == 'mail':
            senders.append(MailSender(section))
        else:
            raise Exception('Unknow section: %s' % section)


def willsend():
    '一小时内只告警一次'

    db = {}
    if os.path.exists(DBPATH):
        f = open(DBPATH, 'r')
        db = pickle.load(f)
        f.close()

    now = datetime.datetime.now()
    lastsend = now - datetime.timedelta(days=365, seconds=100, microseconds=55)
    if 'lastsend' in db:
        lastsend = db['lastsend']

    diff = now - lastsend
    debuglog.info('willsend: lastsend=%s, diff=%s', lastsend, diff)

    total_seconds = diff.days * 24 * 60 * 60
    total_seconds += diff.seconds
    if total_seconds > 60 * 60:
        f = open(DBPATH, 'wb')
        db['lastsend'] = now
        pickle.dump(db, f)
        f.close()
        return True

    return False


def process_results(results):
    for monitor, result in results:
        statlog.info("%s %s", monitor.section, result.succ)
        if result.succ:
            debuglog.info("%s: %s", monitor.section, result)
        else:
            debuglog.error("%s: %s", monitor.section, result)

    title = u'机器告警(zoro)'
    content = ''
    filters = filter(lambda x: not x[1].succ, results)
    for m, r in filters:
        content += '=======================\n'
        content += 'name: %s\n' % m.section
        content += 'description: %s\n' % m

        content += 'error:\n'
        content += '%s\n' % (r.error)
        content += '===\n'

        if r.log:
            content += 'log:\n'
            content += '%s\n' % (r.log)
            content += '===\n'

        content += '=======================\n'

    if filters and willsend():
        for sender in senders:
            sender.send(title, content)


class MonitorThred(threading.Thread):
    def __init__(self, monitor, q):
        threading.Thread.__init__(self)
        self.monitor = monitor
        self.q = q
        self.daemon = True
        self.setDaemon(True)

    def run(self):
        try:
            debuglog.info('task begin: %s', self.monitor.section)
            r = self.monitor.run()
            self.q.put(r)
            debuglog.debug('task end: %s', self.monitor.section)
        except Exception, ex:
            debuglog.debug('task end error: %s', self.monitor.section)
            debuglog.exception(ex)
            self.q.put(MonitorResult(False, error=str(ex)))


def main():
    ps = []
    for m in monitors:
        q = Queue.Queue()
        p = MonitorThred(m, q)
        ps.append((m, p, q))
        p.start()

    results = []
    time.sleep(TASK_TIMEOUT)
    for m, p, q in ps:
        debuglog.info('check p: %s %s', m.section, p.isAlive())

        r = MonitorResult(False, 'process error: get none')
        if not p.isAlive() and  not q.empty():
            r = q.get()

        results.append((m, r))

    process_results(results)


if __name__ == '__main__':
    main()
