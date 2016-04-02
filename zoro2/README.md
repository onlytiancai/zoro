### 单机监控脚本 - zoro

大多时候用户投诉，都是因为监控不到位，没有提前发现问题，做好预警。
所以写了个脚本来满足最基本的单机监控，比如经常发生的磁盘满，进程数
太多，日志文件里大量出错，nginx突然请求量上升，某个后台依赖的http
服务不可访问等。

当发现系统异常时，可以调用一个url回调地址来告警，这个告警api需要
自己去定制实现，比如发送邮件，微信，或集成到内部告警平台。

为防止骚扰, 1小时内多次告警自动收敛，只告警一次，要查询1小时内错误
详情，需要登录机器看错误日志，反正真有问题，肯定要登录机器的。
 

负载告警：5分钟内平均负载大于1告警

```
[monitor:1]
type=load
max=1
```

磁盘使用率告警：任意磁盘使用率超过80%告警

```
[monitor:2]
type=disk
max=80
```

HTTP告警：当本机有服务依赖的某http api不可访问时告警，超时时间是1秒钟

```
[monitor:3]
type=http
url=http://www.baidu.com
timeout=1
```

TCP告警：当本机有服务依赖的某tcp服务不可访问时告警，超时时间是1秒钟

```
[monitor:4]
type=tcp
ip=baidu.com
port=800
timeout=1
```

日志告警：当最近1小时应用日志的错误数超过100时告警

```
[monitor:5]
type=log
logpath=/usr/local/nginx/logs/access.log
timeformat=%d/%b/%Y %H
max=100
keyword=" ERROR "
```

进程告警: 当nginx进程数小于1，大于5时告警

```
[monitor:6]
type=process
keyword="nginx: worker process"
max=5
min=1
```

总进程数告警：当总进程数超过200时告警

```
[monitor:7]
type=process
max=200
```


完整配置示例参考`config.ini`
