# -*- coding: utf8 -*-

import ConfigParser
import multiprocessing
import subprocess
import urllib
import urllib2
import socket
import datetime
import logging
import logging.handlers

cf = ConfigParser.ConfigParser()
cf.read('config.ini')


def logger(name, console=False):
    logpath = cf.get('common', name)
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')

    h = logging.handlers.TimedRotatingFileHandler(logpath, 'D', 1, 10)
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

        cmd = ['/bin/grep', self.keyword]
        grep = subprocess.Popen(cmd, stdout=subprocess.PIPE, stdin=grep.stdout)

        cmd = ['/usr/bin/wc', '-l']
        wc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stdin=grep.stdout)
        wc = int(wc.communicate()[0])

        log = '`grep "%s" %s | grep "%s" | wc -l` = %s ' \
            % (logtime, self.logpath, self.keyword, wc)
        if wc > self.max:
            return MonitorResult(False, error=log)

        return MonitorResult(True, log=log)


class UrlSender(object):
    def __init__(self, section):
        self.url = cf.get(section, 'url')
        self.timeout = 5
        if cf.has_option(section, 'timeout'):
            self.timeout = cf.getfloat(section, 'timeout')

    def send(self, title, content):
        debuglog.debug('urlsender title: %s', title)
        debuglog.debug('urlsender content:\n%s', content)

        data = dict(title=title, content=content)
        postdata = {}
        for k, v in data.iteritems():
            postdata[k] = unicode(v).encode('utf-8')
        postdata = urllib.urlencode(postdata)
        try:
            req = urllib2.Request(self.url, data=postdata)
            rsp = urllib2.urlopen(req, timeout=self.timeout)
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


def process_results(results):
    for monitor, result in results:
        statlog.info("%s %s", monitor.section, result.succ)
        if result.succ:
            debuglog.debug("%s: %s", monitor.section, result)
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

    for sender in senders:
        sender.send(title, content)


def run_monitor(monitor, q):
    try:
        r = monitor.run()
        q.put(r)
    except Exception, ex:
        q.put(MonitorResult(False, error=str(ex)))


def main():
    ps = []
    for m in monitors:
        q = multiprocessing.Queue()
        p = multiprocessing.Process(target=run_monitor, args=(m, q))
        p.daemon = True
        ps.append((m, p, q))
        p.start()

    results = []
    for m, p, q in ps:
        p.join(1000)
        if p.is_alive():
            p.terminate()
            p.join()

        r = MonitorResult(False, 'process error: get none')
        if not q.empty():
            r = q.get()

        results.append((m, r))

    process_results(results)


if __name__ == '__main__':
    main()
