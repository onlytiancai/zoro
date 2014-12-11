#! /usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import smtplib
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from email.header import Header
import json

plugin_args = {}

def init(all_cfg, plugin_cfg):
    if not all(x in plugin_cfg['args'] for x in ['from', 'to', 'smtp_server',
                                                 'smtp_user', 'smtp_pass', 'smtp_ssl']):
        raise Exception("plugin(%s) args Error" % plugin_cfg['type'])
    plugin_args.update(plugin_cfg['args'])


def _get_mail_content(rule, monitor_ret, cfg):
    ret = ''
    ret += u'## 告警内容：\n%s \n\n' % rule['args'].get("title")
    ret += u'## 告警结果：\n%s \n\n' % str(monitor_ret)
    ret += u'## 告警规则：\n%s \n\n' % json.dumps(rule, indent=4)
    return ret


def send(rule, ret, cfg):
    logging.debug("mail send:%s %s", rule, ret)
    try:
        content = _get_mail_content(rule, ret, cfg)
        msg = MIMEText(content, 'plain', 'utf-8')
        msg['Subject'] = Header(u'监控告警：%s' % rule['args'].get("title"), 'utf-8')
        msg['From'] = plugin_args['from']
        msg['To'] = COMMASPACE.join(plugin_args['to'])
        msg['Date'] = formatdate(localtime=True)

        server = smtplib.SMTP(plugin_args['smtp_server'])
        if plugin_args['smtp_ssl'] == 'True':
            server.starttls()
        server.login(plugin_args['smtp_user'], plugin_args['smtp_pass'])
        server.sendmail(plugin_args['from'], plugin_args['to'], msg.as_string())
        server.quit()
    except Exception:
        logging.exception('sender.mail send error:%s', rule)
