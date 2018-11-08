#! /usr/bin/python
# encoding:utf-8

# 配置文件
import ConfigParser
conf = ConfigParser.ConfigParser()
conf.read('config/db_monitor.conf')
# 日志
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logfile = conf.get("log","check_logfile")
fh = logging.FileHandler(logfile,mode='a')
fh.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
fh.setFormatter(formatter)
ch.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(ch)