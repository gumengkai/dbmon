#! /usr/bin/python
# encoding:utf-8

import ConfigParser

import tools as tools
import my_log as my_log
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import os
import send_email as mail

conf = ConfigParser.ConfigParser()

# 间隔固定时间再次发送邮件告警
def is_send_email(alarm_name,tags,url,email_header,alarm_content):
    conf_path = os.path.dirname(os.getcwd())
    conf.read('%s/config/db_monitor.conf' %conf_path)
    receiver = conf.get("email", "receiver").split(',')
    is_send = conf.get("email","is_send")
    next_time_to_send_email = float(conf.get("policy", "next_send_email_time"))
    is_alarm_in_min_sql = "select count(*) from tab_alarm_email_info where tags = '%s' and url='%s' and alarm_type='%s' and email_header = '%s' and timestampdiff(minute,alarm_time,current_timestamp())<%s" % (
        tags,url, alarm_name, email_header,next_time_to_send_email)
    # print is_alarm_in_15min_sql
    is_alarm_in_15min = tools.mysql_query(is_alarm_in_min_sql)
    cnt = is_alarm_in_15min[0][0]
    if cnt == 0 and float(is_send) <> 0:
        try:
            mail.send_email(receiver, email_header, alarm_content)
            my_log.logger.info('成功发送告警邮件: %s 到%s' % (email_header, receiver))
            email_sql = 'insert into tab_alarm_email_info(tags,url,email_header,email_content,alarm_type) value(%s,%s,%s,%s,%s)'
            value = (tags,url, email_header, alarm_content, alarm_name)
            tools.mysql_exec(email_sql, value)
        except Exception, e:
            error_msg = "To %s 发送邮件失败:%s" % (receiver, str(e))
            my_log.logger.error(error_msg)

def check_alarm():
    my_log.logger.info('初始化告警信息表')
    ins_sql = "insert into tab_alarm_info_his select * from tab_alarm_info"
    tools.mysql_exec(ins_sql, '')
    delete_sql = "delete from tab_alarm_info"
    tools.mysql_exec(delete_sql, '')
    check_list = tools.mysql_query(
        "select alarm_name,jdg_value,select_sql,jdg_sql,conf_table,conf_col from tab_alarm_conf where jdg_sql is not null ")
    for each_check in check_list:
        # 取告警名称和阈值
        alarm_name, jdg_value, select_sql, jdg_sql_conf,conf_table,conf_col = each_check
        alarm_name = alarm_name.encode('utf-8')
        my_log.logger.info("开始巡检：%s" %alarm_name)
        # 判断目标表是否采集到告警数据
        select_res = tools.mysql_query(select_sql)
        if select_res[0][0] == 0:
            my_log.logger.info("%s未采集到数据" % alarm_name)
        else:
            #  采集数据阈值检查
            is_judge_sql = ' tags in (select tags from %s where %s =1)' %(conf_table,conf_col)
            jdg_sql = jdg_sql_conf % (jdg_value,is_judge_sql) if jdg_value else jdg_sql_conf % is_judge_sql
            check_res = tools.mysql_query(jdg_sql)
            if check_res == 0:
                my_log.logger.info("%s:正常" % alarm_name)
            else:
                for each in check_res:
                    tags,alarm_url,alarm_content = each
                    alarm_title = tags + ':' + alarm_name
                    alarm_sql = 'insert into tab_alarm_info(tags,url,alarm_type,alarm_header,alarm_content) value(%s,%s,%s,%s,%s)'
                    value = (tags, alarm_url, alarm_name, alarm_title, alarm_content)
                    my_log.logger.warning(alarm_content)
                    tools.mysql_exec(alarm_sql, value)
                    # 发送告警邮件
                    is_send_email(alarm_name, tags, alarm_url, alarm_title, alarm_content)


if __name__ == '__main__':
    check_alarm()

