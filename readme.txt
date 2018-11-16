# db_monitor
python+Django数据库监控平台

开发技术：python，django，bootsrap，html，sql

整体架构：后端多进程数据采集+告警轮询+web前端展示

特色：支持主机、Oracle、MySQL基础数据监控及性能监控，以评分形式展示各项服务健康度，关键指标形成dashboard趋势分析，自定义告警阈值，支持邮件告警，采用celery任务管理机制，集成多个任务维护工具

开发工具版本：
python2.7
django1.9
celery3.1(因在windows环境开发，暂时使用这个版本，部署到Linux会采用celery4)
MySQL-python (1.2.3)
cx-Oracle (6.0.2)

核心功能：
想了想，太多了，Oracle的能想到的都做了，基本可以涵盖所有日常运维、监控内容。主机的主要是CPU，内存，流量一些核心指标，用作参考，MySQL部分的还不是很多，正在着手开发

注：
Oracle top sql功能为存储过程实现，需要先在被监控库执行脚本oracle/scripts/*

示例访问地址：
http://www.dbmon.cn/login/
用户名密码：admin/111111
