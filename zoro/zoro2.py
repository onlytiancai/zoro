# -*- coding: utf8 -*-

import ConfigParser
import subprocess
import urllib2


cf = ConfigParser.ConfigParser()
cf.read('config.ini')

monitors = []

class MonitorResult(object):
    def __init__(self, succ=True, log='', error=''):
        self.succ = succ 
        self.log = log
        self.error = error


class DiskMonitor(object):
    def __init__(self, section):
        self.section = section
        self.max = cf.getint(section, 'max')

    def __str__(self):
        return 'monitor: type=disk, max=%s' % (self.max)

    def run(self):
        output = subprocess.Popen(['/bin/df', '-h'], stdout=subprocess.PIPE).communicate()[0]
        '''
        Filesystem      Size  Used Avail Use% Mounted on
        /dev/vda1        20G  2.3G   17G  13% /
        '''
        lines = output.splitlines()[1:]
        for line in lines:
            arr = line.split()
            diskuse = int(arr[4].replace('%', ''))
            if diskuse > self.max:
                error="%s diskuse > %s%%: %s%%" % (arr[0], self.max, diskuse)
                return MonitorResult(False, error=error)
        
        return MonitorResult(True, log=output)

class LoadMonitor(object):
    def __init__(self, section):
        self.section = section
        self.max = cf.getfloat(section, 'max')

    def __str__(self):
        return 'monitor: type=load, max=%s' % (self.max)

    def run(self):
        output = subprocess.Popen(['/usr/bin/uptime'], stdout=subprocess.PIPE).communicate()[0]
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
            return MonitorResult(True, log="http task:%s error:%s" % (self.url, ex))


class TcpMonitor(object):
    def __init__(self, section):
        self.section = section
        self.ip = cf.get(section, 'ip')
        self.port  = cf.getint(section, 'port')
        self.timeout = 5
        if cf.has_option(section, 'timeout'):
            self.timeout = cf.getfloat(section, 'timeout')

    def __str__(self):
        return 'monitor: type=tcp, ip=%s, port=%s, timeout=%s' \
                % (self.ip, self.port,self.timeout)

    def run(self):
        return MonitorResult()


class LogMonitor(object):
    def __init__(self, section):
        self.section = section
        self.logpath = cf.get(section, 'logpath')
        self.timeformat = cf.get(section, 'timeformat')
        self.max = cf.getfloat(section, 'max')

    def __str__(self):
        return 'monitor: type=log, logpath=%s, timeformat=%s, max=%s' \
                % (self.logpath, self.timeformat, self.max)

    def run(self):
        return MonitorResult()


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
        else:
            raise Exception('Unknow section: %s' % section)

def main():
    for monitor in monitors:
        r = monitor.run()
        if r.succ:
            print 'succ: %s' % monitor
            print '\t', r.log
        else:
            print 'error: %s' % monitor
            print '\t', r.error

if __name__ == '__main__':
    main()
