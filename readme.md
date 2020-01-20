## 说明：该项目已停止开发，请移步新的监控项目，基于前后端分离结构：https://github.com/gumengkai/db_monitor

# 总体介绍

python+Django数据库监控平台

开发技术：python，django(web框架)，AdminLTE(前端模板)

整体架构：后端多进程数据采集+告警轮询+web前端展示+celery任务管理

特色：支持主机、Oracle、MySQL基础数据监控及性能监控，以评分形式展示各项服务健康度，关键指标形成dashboard趋势分析，自定义告警阈值，支持邮件告警，采用celery任务管理机制，

qq交流群：916746047 

新监控Demo(建议chrome访问)：
http://122.51.204.250:8080
用户名密码：admin/111111

# 部署：

如果有想要在内网中部署或者部署过程中碰到问题的可以参考下word版的部署文档，比较详细！

### 1. 安装python2.7(略)
注意安装pip

### 2. 安装mysql5.7(略)
由于用到mysql5.7的json相关函数，所以MySQL版本必须不低于5.7，字符集最好默认设置为utf-8

### 3. 安装rabbitmq
用于celery任务管理  
[root@aliyun dbmon]# yum install erlang  
[root@aliyun dbmon]# yum install rabbitmq-server  
[root@aliyun dbmon]# service rabbitmq-server start  
Starting rabbitmq-server: SUCCESS  
rabbitmq-server.  

### 4. 克隆项目，解压缩
##### 数据库脚本
(必须执行)：setup/mysql/db_monitor.sql & setup/mysql/initdata.sql  
(监控Oracle时在被监控库、监控用户下执行)：setup/oracle/procedure.sql & setup/oracle/table.sql  

##### 安装依赖包
pip install -r requirements.txt

如果要监控Oracle数据库，需要安装Oracle instant client以使用cx_oracle

##### 修改配置文件

-- 总体配置文件，主要修改mysql数据库配置  
config/db_monitor.conf  
[target_mysql]  
host = 172.17.243.119  
port = 3306  
user = root  
password = Mysql@123  
dbname = db_monitor  

--Django配置文件settings.py，修改MySQL配置  
DATABASES = {  
    'default': {  
        'ENGINE': 'django.db.backends.mysql',  
		'NAME': 'db_monitor',  
		'USER': 'root',  
		'PASSWORD': 'mysqld',  
        'HOST':'192.168.48.50',  
		'PORT': '3306',  
    }
}

-- celery配置文件 settings.py  
BROKER_URL = 'amqp://guest:guest@localhost//'
这个如果rabbitmq是默认安装的话，就不需要修改了

##### 同步数据库，建用户
暂时没有做用户/角色体系，可以先通过django自带的admin页面来管理  
[root@aliyun dbmon]# python manage.py migrate  
[root@aliyun dbmon]# python manage.py createsuperuser  

### 5. 启动
--数据采集  
[root@aliyun check_alarm]# python main_check.py  
注：在前端界面添加监控设备
--django  
[root@aliyun dbmon]# python manage.py runserver 0.0.0.0:8000  --自己选择IP和端口号
访问：0.0.0.0:8000/login
--webssh  
[root@aliyun webssh]# python main.py  
注：webssh不可单独访问，必须通过db_monitor的Linux主机概览页面跳转
--celery  
[root@aliyun dbmon]# celery -A dbmon worker -l info  
[root@aliyun dbmon]# celery -A dbmon beat -l info  
### 6. 注意事项

上传了一份我自己在阿里云服务器上部署的记录：install.log，不一定完整，可以参考一下

### 版本说明
服务端:  
centos6.5  
监控客户端： 
linux: centos6.5,centos6.8,redhat7.2  
oracle: oracle11.2.0.4  
mysql: mysql5.6,mysql5.7  

使用其他版本的linux或数据库版本可能会遇到未知问题，待后续适配

