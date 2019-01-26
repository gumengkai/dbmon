#! /usr/bin/python
#coding: utf-8

import smtplib
from email.mime.text import MIMEText
from email.header import Header
import ConfigParser
import os
conf = ConfigParser.ConfigParser()
conf_path = os.path.dirname(os.getcwd())
conf.read('%s/config/db_monitor.conf' %conf_path)

def send_email(receiver,subject,content):
    sender = conf.get("email","sender")
    smtpserver = conf.get("email","smtpserver")
    username = conf.get("email","username")
    password = conf.get("email","password")
    # content = '表空间使用率告警'
    for each in xrange(len(receiver)):
        msg = MIMEText(content, _charset='utf8')  # 中文需参数‘utf-8’，单字节字符不需要
        msg['Subject'] = Header(subject, 'utf-8')
        msg['From'] = conf.get("email", "msg_from")
        msg['To'] = receiver[each]
        smtp = smtplib.SMTP()
        smtp.connect(smtpserver)
        smtp.login(username, password)
        smtp.sendmail(sender, receiver[each], msg.as_string())
        smtp.quit()




