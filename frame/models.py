from django.db import models


import datetime
from datetime import date

# Create your models here.

class EventRecorder(models.Model):
    event_type = models.CharField(max_length=255)
    event_type_color = models.CharField(max_length=255)
    event_section = models.CharField(max_length=255)
    event_content = models.TextField()
    record_time = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'event_recorder'


class TabAlarmConf(models.Model):
    id = models.IntegerField(primary_key=True)
    db_type = models.CharField(max_length=255)
    alarm_name = models.CharField(max_length=255)
    pct_max = models.CharField(max_length=255, blank=True, null=True)
    size_min = models.CharField(max_length=255, blank=True, null=True)
    time_max = models.CharField(max_length=255, blank=True, null=True)
    num_max = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tab_alarm_conf'


class TabAlarmEmailInfo(models.Model):
    tags = models.CharField(max_length=255)
    url = models.CharField(max_length=255)
    alarm_type = models.CharField(max_length=255)
    email_header = models.CharField(max_length=255)
    email_content = models.TextField()
    alarm_time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tab_alarm_email_info'


class TabAlarmInfo(models.Model):
    tags = models.CharField(max_length=255)
    url = models.CharField(max_length=255)
    alarm_type = models.CharField(max_length=255)
    alarm_header = models.CharField(max_length=255)
    alarm_content = models.TextField()
    alarm_time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tab_alarm_info'

class CheckInfo(models.Model):
    id = models.IntegerField(primary_key=True)
    check_tag = models.CharField(max_length=255)
    check_type = models.CharField(max_length=255)
    server_tag = models.CharField(max_length=255)
    check_err_type = models.CharField(max_length=255)
    check_err = models.CharField(max_length=1000)
    begin_time = models.CharField(max_length=255)
    end_time = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'check_info'

class LogCollectConf(models.Model):
    id = models.IntegerField(primary_key=True)
    app_name = models.CharField(max_length=255)
    host = models.CharField(max_length=255)
    user = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    log_name = models.CharField(max_length=255)
    log_path = models.CharField(max_length=1000)

    class Meta:
        managed = False
        db_table = 'log_collect_conf'

class ManyLogs(models.Model):
    id = models.IntegerField(primary_key=True)
    log_type = models.CharField(max_length=255)
    log_info = models.TextField()
    err_info = models.TextField()
    log_time = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'many_logs'

class EasyStartConf(models.Model):
    id = models.IntegerField(primary_key=True)
    oper_type = models.CharField(max_length=255)
    app_name = models.CharField(max_length=255)
    host = models.CharField(max_length=255)
    user = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    do_cmd = models.CharField(max_length=255)
    process_check = models.CharField(max_length=255)
    process_check_result = models.CharField(max_length=255)
    check_log = models.CharField(max_length=255)
    check_log_result = models.CharField(max_length=255)
    oper_time = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'easy_start_conf'

class SqlList(models.Model):
    id = models.IntegerField(primary_key=True)
    sql_no = models.CharField(max_length=255)
    sql_info = models.TextField()
    sql_name = models.CharField(max_length=255)
    db_name = models.CharField(max_length=255)
    result = models.CharField(max_length=255)
    result_color = models.CharField(max_length=255)
    exec_time = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'sql_list'

class MyTask(models.Model):
    id = models.IntegerField(primary_key=True)
    task_id = models.CharField(max_length=255)
    server_type = models.CharField(max_length=255)
    tags = models.CharField(max_length=255)
    oper_type = models.CharField(max_length=255)
    task_name = models.CharField(max_length=255)
    args = models.CharField(max_length=255)
    result = models.CharField(max_length=255)
    start_time = models.DateTimeField(auto_now=False)
    end_time = models.DateTimeField(auto_now=False)
    runtime = models.FloatField()
    state = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'my_task'