### 为什么做这个项目？

写代码写了十几年，遇到了很大的瓶颈，不想学新东西，也不知道做点什么事情有意义。
看了一些国外的开源产品及其团队，很是羡慕，所以决定花长时间开发维护一个开源项目。
好多人都有自己的服务器，服务器运行的是否正常，是大家都会关心的，这个项目就解决这个问题。

### 花两年时间做成一个人人想用的开源软件

[Linus](http://en.wikipedia.org/wiki/Linus_Torvalds)说过做开源项目最重要的坚持、专注，
所以该项目决心成为一个长期的项目，计划用两年的时间打磨成一个人人都想用的开源软件。
今天是2013年10月10日。

### 如何确定项目是否有意义

这个项目到底有没有意义，会不会有人用，我现在真的不知道，如何确认这个问题，我也不清楚。
现在外部监控(如[D监控](https://support.dnspod.cn/Kb/showarticle/tsid/16/))和内部监控(如[Newrelic](http://newrelic.com/))的产品都有很多。
这个项目想做一个很简单就能安装使用的本机监控软件，不需要运营一个网站，而且强调扩展性，让人们去开发各种插件满足不同的监控需求以及和自己的监控系统集成。

### 如何找到一起开发的人

得先找到认可该项目理念和目标的人，再就是技能，性格上能够互补，能踏实做事的人。

### 如何让外国人关注和使用

反正目前我对英语是一窍不通，稳当和注释都只能用中文，后续如何项目真的有用了，再找人翻译吧。

### 如何让项目显得专业，可以信赖

[以正确的方式开源 Python 项目](http://www.oschina.net/translate/open-sourcing-a-python-project-the-right-way)，这篇文章是我今年看到的针对开发Python项目最全面详细的文章，包括项目结构，打包，测试，文档，自动构建等都很专业，我决定好好实践一下。

### 我有很多机器，如何集中的管理报警

报警时提供主机名，不通机器的报警能够区分，后续可以做一个单独收集报警的网站，目前也做了一个[Demo](http://warnings.sinaapp.com/default)。

### 如何在机器发生问题时收集有用且够用的信息

报警时最好要把当前主机的环境信息，配置信息，资源使用情况，甚至相关日志等收集起来，这样用户看到邮件后就可以大体知道问题原因。
这块儿要慢慢摸索，最终达到智能的效果。