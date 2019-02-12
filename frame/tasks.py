#! /usr/bin/python
# encoding:utf-8

# Create your tasks here

from __future__ import absolute_import,unicode_literals
from celery import shared_task
import frame.oracle_do as oracle
import frame.oracle_backup as oracle_bak

import frame.mysql_do as mysql
import frame.mysql_backup as mysql_bak
import frame.mysql_install as mysql_ins

import uuid
import frame.tools as tools

@shared_task
def add(x,y):
    return x+y


