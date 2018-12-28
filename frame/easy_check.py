#! /usr/bin/python
# encoding:utf-8

import tools as tools
import datetime
import time
from pyExcelerator import *
import os

import sys
default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)

import xlrd
from xlutils.copy import copy

def ora_check(tags_l,begin_time,end_time,file_name,file_tag):
    # 写excel
    file_path = os.getcwd() + '/check_result/'
    template = 'oracheck.xls'
    rb = xlrd.open_workbook(file_path+template, formatting_info=True)
    wb = copy(rb)
    row = 1
    for tags in tags_l:
        ws = wb.get_sheet(0)
        errinfo = ''
        check_txt_file = file_path + '/oracheck_' + file_tag + '.txt'
        check_txt =file(check_txt_file,'a+')
        print >> check_txt, '*******oracle数据库：%s 开始时间：%s 结束时间：%s *******\n' % (tags,begin_time,end_time)
        # 检查连接数
        # 当前连接数
        print >> check_txt, '-------连接数-------'
        current_conn_sql = tools.mysql_query("select percent_process from oracle_db where tags= '%s'" % tags)
        current_conn = int(current_conn_sql[0][0])
        # 最大连接数
        para_conn_sql = tools.mysql_query("select max_process from oracle_db where tags= '%s'" % tags)
        para_conn = int(para_conn_sql[0][0])
        print >> check_txt, '总连接数：%s' % para_conn
        # 指定时间段内连接数使用情况]
        conn_sql = tools.mysql_query(
            "select instance_name, max(percent_process),min(percent_process),avg(percent_process) from oracle_db_his where tags= '%s' and DATE_FORMAT(chk_time,'%%Y-%%m-%%d %%H:%%i:%%S')> '%s' and DATE_FORMAT(chk_time,'%%Y-%%m-%%d %%H:%%i:%%S') < '%s'  group by instance_name" % (
            tags, begin_time, end_time))
        instance_name = conn_sql[0][0]
        max_conn = conn_sql[0][1]
        min_conn = conn_sql[0][2]
        avg_conn = round(conn_sql[0][3], 2)
        conn_range = '最大使用率：%s%%,\n' % max_conn + '最小使用率：%s%%,\n' % min_conn + '平均使用率：%s%%,\n' % avg_conn
        print >> check_txt, '最大使用率：%s 最小使用率：%s 平均使用率：%s \n' % (max_conn,min_conn,avg_conn)
        if max_conn > 10:
            conn_errinfo = '连接数最大使用率%s%%,超过10%%\n' %max_conn
            insert_sql = "insert into check_info(check_tag,check_type,server_tag,check_err_type,check_err,begin_time,end_time) values(%s,%s,%s,%s,%s,%s,%s)"
            value = (
                file_tag, 'Oracle数据库', tags,'连接数', conn_errinfo,begin_time,end_time)
            tools.mysql_exec(insert_sql, value)
            errinfo = conn_errinfo



        # 检查表空间
        print >> check_txt, '-------表空间-------'
        tbs_sql = tools.mysql_query(
            "select tbs_name,free_gb,pct_used from oracle_tbs where tags = '%s' and pct_used > 90 and free_gb < 5" % tags)
        tbsinfo = ''
        err_tbsinfo = ''
        for tbs in tbs_sql:
            tbs_name = str(tbs[0].encode("utf-8"))
            free_gb = float(tbs[1].encode("utf-8"))
            pct_used = tbs[2]
            each_tbs_info = '表空间名称：%s,剩余空间：%sGB,使用率：%s%% \n' % (tbs_name, free_gb, pct_used)
            each_err_tbsinfo = '%s表空间,' %tbs_name
            if free_gb < 5:
                each_err_tbsinfo = each_err_tbsinfo + '剩余空间%sG,小于5G  ' %free_gb
            if pct_used > 90:
                each_err_tbsinfo = each_err_tbsinfo + '使用率%s%%,大于90%%' % pct_used
            tbsinfo = tbsinfo + each_tbs_info
            err_tbsinfo = err_tbsinfo + each_err_tbsinfo + '\n'
            insert_sql = "insert into check_info(check_tag,check_type,server_tag,check_err_type,check_err,begin_time,end_time) values(%s,%s,%s,%s,%s,%s,%s)"
            value = (
                file_tag, 'Oracle数据库', tags, '表空间', each_err_tbsinfo, begin_time, end_time)
            tools.mysql_exec(insert_sql, value)
        errinfo = errinfo + err_tbsinfo
        if not tbsinfo:
            err_tbsinfo = '正常'
        print >> check_txt, tbsinfo


        # 检查Undo表空间
        print >> check_txt, '-------undo表空间-------'
        undo_tbs_sql = tools.mysql_query(
            "select undo_tbs_name,max(used_mb),max(pct_used),min(pct_used),avg(pct_used) from oracle_undo_tbs_his where tags = '%s' and DATE_FORMAT(chk_time,'%%Y-%%m-%%d %%H:%%i:%%S')> '%s' and DATE_FORMAT(chk_time,'%%Y-%%m-%%d %%H:%%i:%%S') < '%s' group by undo_tbs_name" % (
            tags, begin_time, end_time))
        undotbsinfo = ''
        err_undotbsinfo = ''
        if undo_tbs_sql:
            for undotbs in undo_tbs_sql:
                undotbs_name = str(undotbs[0].encode("utf-8"))
                used_mb = float(undotbs[1].encode("utf-8"))
                max_pct_used = float(undotbs[2].encode("utf-8"))
                min_pct_used = float(undotbs[3].encode("utf-8"))
                avg_pct_used = round(float(undotbs[4]), 2)
                each_undotbs_info = 'UNDO表空间名称：%s,已使用空间：%sMB,最大使用率：%s%% 最小使用率：%s%%  平均使用率：%s%% \n' % (
                    undotbs_name, used_mb, max_pct_used, min_pct_used, avg_pct_used)
                each_err_undotbsinfo = ''
                if max_pct_used > 1:
                    each_err_undotbsinfo = '%s表空间,' % undotbs_name
                    each_err_undotbsinfo = each_err_undotbsinfo + ' 最大使用率%s%%,大于90%%' % max_pct_used
                    err_undotbsinfo = err_undotbsinfo + each_err_undotbsinfo + '\n'
                    insert_sql = "insert into check_info(check_tag,check_type,server_tag,check_err_type,check_err,begin_time,end_time) values(%s,%s,%s,%s,%s,%s,%s)"
                    value = (
                        file_tag, 'Oracle数据库', tags, 'undo表空间', each_err_undotbsinfo, begin_time, end_time)
                    tools.mysql_exec(insert_sql, value)
                undotbsinfo = undotbsinfo + each_undotbs_info

        errinfo = errinfo + err_undotbsinfo

        print >> check_txt, undotbsinfo
        # 检查临时表空间
        print >> check_txt, '-------临时表空间-------'
        tmp_tbs_sql = tools.mysql_query(
            "select tmp_tbs_name,max(used_mb),max(pct_used),min(pct_used),avg(pct_used) from oracle_tmp_tbs_his where tags = '%s' and DATE_FORMAT(chk_time,'%%Y-%%m-%%d %%H:%%i:%%S')> '%s' and DATE_FORMAT(chk_time,'%%Y-%%m-%%d %%H:%%i:%%S') < '%s' group by tmp_tbs_name" % (
                tags, begin_time, end_time))
        tmptbsinfo = ''
        err_tmptbsinfo = ''
        if tmptbsinfo:
            for tmptbs in tmp_tbs_sql:
                tmptbs_name = str(tmptbs[0].encode("utf-8"))
                used_mb = float(tmptbs[1].encode("utf-8"))
                max_pct_used = float(tmptbs[2].encode("utf-8"))
                min_pct_used = float(tmptbs[3].encode("utf-8"))
                avg_pct_used = round(float(tmptbs[4]), 2)
                each_tmptbs_info = 'TMP表空间名称：%s,使用空间：%sMB,最大使用率：%s%% 最小使用率：%s%%  平均使用率：%s%% \n' % (
                    tmptbs_name, used_mb, max_pct_used, min_pct_used, avg_pct_used)
                each_err_tmptbsinfo = ''
                if max_pct_used > 1:
                    each_err_tmptbsinfo = '%s表空间,' % tmptbs_name
                    each_err_tmptbsinfo = each_err_tmptbsinfo + ' 最大使用率%s%%,大于90%%' % max_pct_used
                    err_tmptbsinfo = err_tmptbsinfo + each_err_tmptbsinfo + '\n'
                    insert_sql = "insert into check_info(check_tag,check_type,server_tag,check_err_type,check_err,begin_time,end_time) values(%s,%s,%s,%s,%s,%s,%s)"
                    value = (
                        file_tag, 'Oracle数据库', tags, 'TMP表空间', each_err_tmptbsinfo, begin_time, end_time)
                    tools.mysql_exec(insert_sql, value)
                tmptbsinfo = tmptbsinfo + each_tmptbs_info

                print >> check_txt, undotbsinfo

        errinfo = errinfo + err_tmptbsinfo

        # 检查cpu使用率,内存使用率
        # 当前使用率
        linux_used = tools.mysql_query(
            "select cpu_used,mem_used from os_info where host = (select host from tab_oracle_servers where tags =  '%s')" % tags)
        cpu_used = float(linux_used[0][0])
        mem_used = float(linux_used[0][1])
        #
        cpu_range = tools.mysql_query(
            "select max(cpu_used),min(cpu_used),avg(cpu_used),max(mem_used),min(mem_used),avg(mem_used) from os_info_his where host = (select host from tab_oracle_servers where tags =  '%s') and DATE_FORMAT(chk_time,'%%Y-%%m-%%d %%H:%%i:%%S')> '%s' and DATE_FORMAT(chk_time,'%%Y-%%m-%%d %%H:%%i:%%S') < '%s'" % (
                tags, begin_time, end_time))
        cpu_max = round(float(cpu_range[0][0]), 2)
        cpu_min = round(float(cpu_range[0][1]), 2)
        cpu_avg = round(float(cpu_range[0][2]), 2)
        mem_max = round(float(cpu_range[0][3]), 2)
        mem_min = round(float(cpu_range[0][4]), 2)
        mem_avg = round(float(cpu_range[0][5]), 2)
        print >> check_txt, '-------cpu使用率-------'
        cpu_range_value = '最大使用率：%s%%,\n' % cpu_max + '最小使用率：%s%%,\n' % cpu_min + '平均使用率：%s%%,\n' % cpu_avg
        print >> check_txt, cpu_range_value
        if cpu_max > 10:
            cpu_errinfo = ' CPU最大使用率%s%%,超过10%%\n' % cpu_max
            insert_sql = "insert into check_info(check_tag,check_type,server_tag,check_err_type,check_err,begin_time,end_time) values(%s,%s,%s,%s,%s,%s,%s)"
            value = (
                file_tag, 'Oracle数据库', tags, 'CPU使用率', cpu_errinfo, begin_time, end_time)
            tools.mysql_exec(insert_sql, value)
            errinfo = errinfo + cpu_errinfo
        print >> check_txt, '-------内存使用率-------'
        mem_range_value = '最大使用率：%s%%,\n' % mem_max + '最小使用率：%s%%,\n' % mem_min + '平均使用率：%s%%,\n' % mem_avg
        print >> check_txt, mem_range_value
        if mem_max > 10:
            mem_errinfo = '内存最大使用率%s%%,超过10%%\n' % mem_max
            insert_sql = "insert into check_info(check_tag,check_type,server_tag,check_err_type,check_err,begin_time,end_time) values(%s,%s,%s,%s,%s,%s,%s)"
            value = (
                file_tag, 'Oracle数据库', tags, '内存使用率', mem_errinfo, begin_time, end_time)
            tools.mysql_exec(insert_sql, value)
            errinfo = errinfo + mem_errinfo

        ws.write(row, 0, begin_time)
        ws.write(row, 1, end_time)
        ws.write(row, 2, tags)
        ws.write(row, 3, instance_name)
        ws.write(row, 4, current_conn)
        ws.write(row, 5, para_conn)
        ws.write(row, 6, conn_range)
        ws.write(row, 7, unicode('正常', 'utf-8'))
        ws.write(row, 8, unicode(tbsinfo, 'utf-8'))
        ws.write(row, 9, unicode(undotbsinfo, 'utf-8'))
        ws.write(row, 10, unicode(tmptbsinfo, 'utf-8'))
        ws.write(row, 11, unicode('正常', 'utf-8'))
        ws.write(row, 12, unicode('正常', 'utf-8'))
        ws.write(row, 13, unicode('正常', 'utf-8'))
        ws.write(row, 14, unicode(cpu_range_value, 'utf-8'))
        ws.write(row, 15, unicode(mem_range_value, 'utf-8'))

        check_path = os.getcwd() + '\check_result' + '\\'
        wb.save(check_path + file_name)
        print >> check_txt, '-------%s巡检异常-------' % tags
        print >> check_txt, errinfo
        check_txt.close()

        row += 1





