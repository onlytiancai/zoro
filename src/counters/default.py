# -*- coding: utf-8 -*-
import psutil


def get_sysinfo():
    result = {}
    result['cpu_utilization'] = psutil.cpu_percent()
    result['mem_utilization'] = psutil.virtual_memory().percent
    result['swap_utilization'] = psutil.swap_memory().percent
    for part in psutil.disk_partitions(all=False):
        r = psutil.disk_usage(part.mountpoint)
        result['disk_utilization(%s)' % part.mountpoint] = r.percent
    for k, v in psutil.disk_io_counters(True).items():
        if k.startswith('dm'):
            continue
        result['disk_io_read_bytes(%s)' % k] = v.read_bytes
        result['disk_io_write_bytes(%s)' % k] = v.write_bytes
    for k, v in psutil.net_io_counters(True).items():
        if not k.startswith('eth'):
            continue
        result['net_io_bytes_sent(%s)' % k] = v.bytes_sent
        result['net_io_bytes_recv(%s)' % k] = v.bytes_recv
    return result


class Counter(object):
    'Counter插件类，必须使用Counter作为类名'
    
    def __init__(self, options):
        '插件初始化方法，options是插件配置数据'
        self.options = options

    def get_data(self):
        '插件专用方法，必须返回一个字典'
        return get_sysinfo()


if __name__ == '__main__':
    import pprint
    pprint.pprint(get_sysinfo())
