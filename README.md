## Zoro 

我们的目标是让每一台服务器都安装有zoro。

### 简单介绍###

你的网站，VPS，服务器的性能，业务都需要进行监控，并在异常的时候及时通知你。

zoro用来定时收集你服务器运行状态、性能、业务等信息，根据你定义好的规则，发现异常后通知你。

### 快速上手

下载安装

    git clone https://github.com/onlytiancai/zoro.git

    cd zoro 
    pip install -r requirement.txt

    cd src

打开config.ini，修改报警邮件配置

    [sender:mail]
    name = mail 
    smtphost = smtp.163.com
    username = sendwarnings@163.com
    password = password
    from = sendwarnings@163.com
    ;可以用逗号隔开写多个报警收件人
    to = wawasoft@qq.com
    ssl = False
    ;每小时最多发送多少报警
    one_hour_max_send = 1

配置主机的基本报警规则

    [rule:default]
    name = default
    ;主机名，对外发送报警时，区分多台机器
    host = wawahost
    ;以下每行为一个报警规则，格式为"计数器名称 阈值 超过阈值最大次数 报警的标题"
    rule1 = cpu_utilization 70 5 CPU使用率连续5次超过70%
    rule2 = mem_utilization 70 5 内存使用率连续5次超过70%
    rule3 = swap_utilization 70 5 交换分区使用率连续5次超过70%
    rule4 = disk_utilization 70 5 磁盘使用率连续5次超过70%

如果要确保本机必须监听某些端口，做如下配置

    [rule:tcpport]
    name = tcpport 
    host = wawahost
    ;格式为"ip port 报警的标题"
    rule1 = 127.0.0.1 80 nginx端口挂掉
    rule2 = 127.0.0.1 27017 mongodb端口挂掉
    rule3 = 127.0.0.1 3306 mysql端口挂掉

如果要确保本机必须运行某些进程，做如下配置

    [rule:process]
    name = process 
    host = wawahost
    ;格式为"进程cmdline的正则匹配模式 报警的标题", 报警标题为最后一个空格之后的文字
    rule1 = gunicorn mainweb:wsgiapp.*-k gevent 检测到wsgiapp进程不存在

运行zoro

    setsid python zoro_main.py &

可以睡个好觉了，服务有问题你会收到通知的。

小技巧

1. 最好专门申请一个独立的邮箱用来发送报警，163,qq都可以免费注册邮箱。
1. 接收报警的邮箱推荐用qq邮箱，引起如果你开通了微信的话，收到邮件后手机会有提醒。


### 其它

本软件默认功能能满足大多数用户的基本需求，但它很容易扩展，
如果你有兴趣进一步了解并参与这个项目，可以看[详细文档](https://github.com/onlytiancai/zoro/blob/master/docs/details.md)。

如果你有什么疑问，可以[给我提issue](https://github.com/onlytiancai/zoro/issues)
