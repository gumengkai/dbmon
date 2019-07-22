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
    file_path = os.path.dirname(os.getcwd()) + '/dbmon/check_result/'
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

        # 基础信息
        ws.write(row, 0, begin_time)
        ws.write(row, 1, end_time)
        ws.write(row, 2, tags)

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
            "select instance_name, max(percent_process),min(percent_process),avg(percent_process) from oracle_db_his where instance_name is not null and tags= '%s' and DATE_FORMAT(chk_time,'%%Y-%%m-%%d %%H:%%i:%%S')> '%s' and DATE_FORMAT(chk_time,'%%Y-%%m-%%d %%H:%%i:%%S') < '%s'  group by instance_name" % (
            tags, begin_time, end_time))
        instance_name = conn_sql[0][0]
        max_conn = float(conn_sql[0][1].encode("utf-8"))
        min_conn = conn_sql[0][2]
        avg_conn = round(conn_sql[0][3], 2)
        conn_range = '最大使用率：%s%%,\n' % max_conn + '最小使用率：%s%%,\n' % min_conn + '平均使用率：%s%%,\n' % avg_conn
        print >> check_txt, '最大使用率：%s 最小使用率：%s 平均使用率：%s \n' % (max_conn,min_conn,avg_conn)
        if max_conn > 80:
            conn_errinfo = '连接数最大使用率%s%%,超过80%%\n' %max_conn
            insert_sql = "insert into check_info(check_tag,check_type,server_tag,check_err_type,check_err,begin_time,end_time) values(%s,%s,%s,%s,%s,%s,%s)"
            value = (
                file_tag, 'Oracle数据库', tags,'连接数', conn_errinfo,begin_time,end_time)
            tools.mysql_exec(insert_sql, value)
            errinfo = conn_errinfo
        # 实例名
        ws.write(row, 3, instance_name)
        # 连接数信息
        ws.write(row, 4, current_conn)
        ws.write(row, 5, para_conn)
        ws.write(row, 6, max_conn )
        ws.write(row, 7, avg_conn )
        ws.write(row, 8, min_conn )

        # ASM信息
        ws.write(row, 9, unicode('无', 'utf-8'))

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
            if free_gb < 1:
                each_err_tbsinfo = each_err_tbsinfo + '剩余空间%sG,小于1G  ' %free_gb
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
        # 表空间信息
        ws.write(row, 10, unicode(tbsinfo, 'utf-8'))


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
                max_undo_used = float(undotbs[2].encode("utf-8"))
                min_undo_used = float(undotbs[3].encode("utf-8"))
                avg_undo_used = round(float(undotbs[4]), 2)
                each_undotbs_info = 'UNDO表空间名称：%s,已使用空间：%sMB,最大使用率：%s%% 最小使用率：%s%%  平均使用率：%s%% \n' % (
                    undotbs_name, used_mb, max_undo_used, min_undo_used, avg_undo_used)
                each_err_undotbsinfo = ''
                if max_undo_used > 90:
                    each_err_undotbsinfo = '%s表空间,' % undotbs_name
                    each_err_undotbsinfo = each_err_undotbsinfo + ' 最大使用率%s%%,大于90%%' % max_undo_used
                    err_undotbsinfo = err_undotbsinfo + each_err_undotbsinfo + '\n'
                    insert_sql = "insert into check_info(check_tag,check_type,server_tag,check_err_type,check_err,begin_time,end_time) values(%s,%s,%s,%s,%s,%s,%s)"
                    value = (
                        file_tag, 'Oracle数据库', tags, 'undo表空间', each_err_undotbsinfo, begin_time, end_time)
                    tools.mysql_exec(insert_sql, value)
                undotbsinfo = undotbsinfo + each_undotbs_info
            # undo表空间信息
            ws.write(row, 11, undotbs_name)
            ws.write(row, 12, max_undo_used)
            ws.write(row, 13, avg_undo_used)
            ws.write(row, 14, min_undo_used)
        errinfo = errinfo + err_undotbsinfo
        print >> check_txt, undotbsinfo

        # 检查临时表空间
        print >> check_txt, '-------临时表空间-------'
        tmp_tbs_sql = tools.mysql_query(
            "select tmp_tbs_name,max(used_mb),max(pct_used),min(pct_used),avg(pct_used) from oracle_tmp_tbs_his where tags = '%s' and DATE_FORMAT(chk_time,'%%Y-%%m-%%d %%H:%%i:%%S')> '%s' and DATE_FORMAT(chk_time,'%%Y-%%m-%%d %%H:%%i:%%S') < '%s' group by tmp_tbs_name" % (
                tags, begin_time, end_time))
        tmptbsinfo = ''
        err_tmptbsinfo = ''
        if tmp_tbs_sql:
            for tmptbs in tmp_tbs_sql:
                tmptbs_name = str(tmptbs[0].encode("utf-8"))
                print tmptbs_name
                used_mb = float(tmptbs[1].encode("utf-8"))
                max_temp_used = float(tmptbs[2].encode("utf-8"))
                min_temp_used = float(tmptbs[3].encode("utf-8"))
                avg_temp_used = round(float(tmptbs[4]), 2)
                each_tmptbs_info = 'TMP表空间名称：%s,使用空间：%sMB,最大使用率：%s%% 最小使用率：%s%%  平均使用率：%s%% \n' % (
                    tmptbs_name, used_mb, max_temp_used, min_temp_used, avg_temp_used)
                each_err_tmptbsinfo = ''
                if max_temp_used > 90:
                    each_err_tmptbsinfo = '%s表空间,' % tmptbs_name
                    each_err_tmptbsinfo = each_err_tmptbsinfo + ' 最大使用率%s%%,大于90%%' % max_temp_used
                    err_tmptbsinfo = err_tmptbsinfo + each_err_tmptbsinfo + '\n'
                    insert_sql = "insert into check_info(check_tag,check_type,server_tag,check_err_type,check_err,begin_time,end_time) values(%s,%s,%s,%s,%s,%s,%s)"
                    value = (
                        file_tag, 'Oracle数据库', tags, 'TMP表空间', each_err_tmptbsinfo, begin_time, end_time)
                    tools.mysql_exec(insert_sql, value)
                tmptbsinfo = tmptbsinfo + each_tmptbs_info
                print >> check_txt, undotbsinfo
                # temp表空间信息
                ws.write(row, 15, tmptbs_name)
                ws.write(row, 16, max_temp_used)
                ws.write(row, 17, avg_temp_used)
                ws.write(row, 18, min_temp_used)

        errinfo = errinfo + err_tmptbsinfo

        # 文件系统、后台日志、监听日志
        ws.write(row, 19, unicode('正常', 'utf-8'))
        ws.write(row, 20, unicode('正常', 'utf-8'))
        ws.write(row, 21, unicode('正常', 'utf-8'))

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
        if cpu_max > 80:
            cpu_errinfo = ' CPU最大使用率%s%%,超过80%%\n' % cpu_max
            insert_sql = "insert into check_info(check_tag,check_type,server_tag,check_err_type,check_err,begin_time,end_time) values(%s,%s,%s,%s,%s,%s,%s)"
            value = (
                file_tag, 'Oracle数据库', tags, 'CPU使用率', cpu_errinfo, begin_time, end_time)
            tools.mysql_exec(insert_sql, value)
            errinfo = errinfo + cpu_errinfo
        # CPU使用率信息
        ws.write(row, 22, cpu_max)
        ws.write(row, 23, cpu_avg)
        ws.write(row, 24, cpu_min)
        print >> check_txt, '-------内存使用率-------'
        mem_range_value = '最大使用率：%s%%,\n' % mem_max + '最小使用率：%s%%,\n' % mem_min + '平均使用率：%s%%,\n' % mem_avg
        print >> check_txt, mem_range_value
        if mem_max > 80:
            mem_errinfo = '内存最大使用率%s%%,超过80%%\n' % mem_max
            insert_sql = "insert into check_info(check_tag,check_type,server_tag,check_err_type,check_err,begin_time,end_time) values(%s,%s,%s,%s,%s,%s,%s)"
            value = (
                file_tag, 'Oracle数据库', tags, '内存使用率', mem_errinfo, begin_time, end_time)
            tools.mysql_exec(insert_sql, value)
            errinfo = errinfo + mem_errinfo
        # 内存使用率信息
        ws.write(row, 25, mem_max )
        ws.write(row, 26, mem_avg )
        ws.write(row, 27, mem_min )
        # 连接、CPU、内存/是否满足本地高可用，备份是否正常，是否有失效索引，巡检发现问题
        ws.write(row, 28, unicode('是', 'utf-8'))
        ws.write(row, 29, unicode('是', 'utf-8'))
        ws.write(row, 30, unicode('是', 'utf-8'))
        ws.write(row, 31, unicode('是', 'utf-8'))
        ws.write(row, 32, unicode('否', 'utf-8'))
        ws.write(row, 33, unicode('无', 'utf-8'))

        check_path = os.path.dirname(os.getcwd()) + '/dbmon/check_result/'
        wb.save(check_path + file_name)
        print >> check_txt, '-------%s巡检异常-------' % tags
        print >> check_txt, errinfo
        check_txt.close()

        row += 1

