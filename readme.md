# 总体介绍

python+Django数据库监控平台

开发技术：python，django(web框架)，AdminLTE(前端模板)

整体架构：后端多进程数据采集+告警轮询+web前端展示+celery任务管理

特色：支持主机、Oracle、MySQL基础数据监控及性能监控，以评分形式展示各项服务健康度，关键指标形成dashboard趋势分析，自定义告警阈值，支持邮件告警，采用celery任务管理机制，

核心功能：
想了想，太多了，Oracle的能想到的都做了，基本可以涵盖所有日常运维、监控内容。主机的主要是CPU，内存，流量一些核心指标，用作参考，MySQL部分的还不是很多，正在着手开发

示例访问地址：
http://www.dbmon.cn/login/
用户名密码：admin/111111

webssh用户名密码：
192.168.48.10 oracle/oracle
192.168.48.50 mysql/mysqld

最后，关于自动化运维里面的工具包，还没有在生产环境应用过，有一些功能上还有些问题，建议不要在正式环境使用，有几个工具如安装数据库、备份管理都还没完善，
请谨慎使用,巡检这个功能暂时也很积鸡肋...

建了个qq群：916746047 有一些好的需求、想法可以提给我，会考虑加进去，或者安装部署、使用过程中碰到的问题，都可以反馈给我

# 部署：

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

### 启动
--数据采集
[root@aliyun check_alarm]# python main_check.py  
--django
[root@aliyun dbmon]# python manage.py runserver  
--webssh
[root@aliyun webssh]# python main.py
--celery
[root@aliyun dbmon]# celery -A dbmon worker -l info  
[root@aliyun dbmon]# celery -A dbmon beat -l info  
### 注意事项
webssh页面中的url需要根据所启动webssh服务的信息手工修改下：  
templates/show_linux.html:
function pop(m,n){  
    layer.open({  
    type: 2 //此处以iframe举例  
    ,title: 'webssh_'+m  
    ,area: ['700px', '550px']  
    ,shade: 0  
    ,maxmin: true,  
    content: ['http://4e38iojldn.51http.tech?host='+n,],  
    btn: ['关闭所有'] //只是为了演示  
    ,btn2: function(){  
      layer.closeAll();  
    }  
    ,zIndex: layer.zIndex //重点1  
    ,success: function(layero){  
      layer.setTop(layero); //重点2  
    },  
   });  
}

另外，上传了一份我自己在阿里云父服务器上部署的记录：install.log，不一定完整，可以参考一下


