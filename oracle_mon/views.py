#! /usr/bin/python
# encoding:utf-8

from django.shortcuts import render

from django.shortcuts import render,render_to_response
from django.http import HttpResponse, HttpResponseRedirect

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# Create your views here.
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from django.http import HttpResponse
import datetime
from frame import tools
# 配置文件
import ConfigParser
import base64
import frame.models as models_frame
import oracle_mon.models as models_oracle
import frame.oracle_do as ora_do
# Create your views here.


@login_required(login_url='/login')
def oracle_monitor(request):
    messageinfo_list = models_frame.TabAlarmInfo.objects.all()
    tagsinfo = models_oracle.TabOracleServers.objects.all().order_by('tags')

    tagsdefault = request.GET.get('tagsdefault')
    if not tagsdefault:
        tagsdefault = models_oracle.TabOracleServers.objects.order_by('tags')[0].tags

    conn_range_default = request.GET.get('conn_range_default')
    if not conn_range_default:
        conn_range_default = '1小时'.decode("utf-8")

    undo_range_default = request.GET.get('undo_range_default')
    if not undo_range_default:
        undo_range_default = '1小时'.decode("utf-8")

    tmp_range_default = request.GET.get('tmp_range_default')
    if not tmp_range_default:
        tmp_range_default = '1小时'.decode("utf-8")

    ps_range_default = request.GET.get('ps_range_default')
    if not ps_range_default:
        ps_range_default = '1小时'.decode("utf-8")

    conn_begin_time = tools.range(conn_range_default)
    undo_begin_time = tools.range(undo_range_default)
    tmp_begin_time = tools.range(tmp_range_default)
    ps_begin_time = tools.range(ps_range_default)

    end_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # 取当前数据库状态
    try:
        oracle_curr = models_oracle.OracleDb.objects.filter(tags=tagsdefault).get(
            tags=tagsdefault, )
    except models_oracle.OracleDb.DoesNotExist:
        oracle_curr = \
            models_oracle.OracleDbHis.objects.filter(tags=tagsdefault).order_by(
                '-chk_time')[0]
    # 取上一次有效采集的数据
    try:
        try:
            oracleinfo = models_oracle.OracleDb.objects.filter(tags=tagsdefault, percent_process__isnull=False).get(tags=tagsdefault,)
        except models_oracle.OracleDb.DoesNotExist:
            oracleinfo = \
            models_oracle.OracleDbHis.objects.filter(tags=tagsdefault, percent_process__isnull=False).order_by(
                '-chk_time')[0]
    except Exception, e:
        oracleinfo = \
            models_oracle.OracleDbHis.objects.filter(tags=tagsdefault).order_by(
                '-chk_time')[0]

    if oracle_curr.mon_status == 'connected':
        check_status = 'success'
        oracle_status = '在线'
    else:
        check_status = 'danger'
        oracle_status = '离线'


    eventinfo = models_oracle.OracleDbEvent.objects.filter(tags=tagsdefault)
    lockinfo = models_oracle.OracleLock.objects.filter(tags=tagsdefault)

    conngrow = models_oracle.OracleDbHis.objects.filter(tags=tagsdefault, percent_process__isnull=False).filter(
        chk_time__gt=conn_begin_time, chk_time__lt=end_time).order_by('-chk_time')
    conngrow_list = list(conngrow)
    conngrow_list.reverse()

    try:
        undoinfo = models_oracle.OracleUndoTbs.objects.get(tags=tagsdefault)
    except models_oracle.OracleUndoTbs.DoesNotExist:
        undoinfo =  models_oracle.OracleUndoTbsHis.objects.filter(tags=tagsdefault, pct_used__isnull=False).order_by('-chk_time')
        if not undoinfo:
            models_oracle.OracleUndoTbsHis.objects.create(tags=tagsdefault,undo_tbs_name='UNDOTBS1', total_mb=0, used_mb=0,
                                                        pct_used=0,rate_level='green')
        undoinfo = models_oracle.OracleUndoTbsHis.objects.filter(tags=tagsdefault, pct_used__isnull=False).order_by('-chk_time')[0]


    undogrow = models_oracle.OracleUndoTbsHis.objects.filter(tags=tagsdefault, pct_used__isnull=False).filter(
        chk_time__gt=undo_begin_time, chk_time__lt=end_time).order_by('-chk_time')
    undogrow_list = list(undogrow)
    undogrow_list.reverse()

    try:
        tmpinfo = models_oracle.OracleTmpTbs.objects.get(tags=tagsdefault,tmp_tbs_name='TEMP')
    except models_oracle.OracleTmpTbs.DoesNotExist:
        tmpinfo =  models_oracle.OracleTmpTbsHis.objects.filter(tags=tagsdefault, pct_used__isnull=False).order_by('-chk_time')
        if not tmpinfo:
            models_oracle.OracleTmpTbsHis.objects.create(tags=tagsdefault, tmp_tbs_name='UNDOTBS1', total_mb=0,
                                                          used_mb=0,
                                                          pct_used=0, rate_level='green')
        tmpinfo = models_oracle.OracleTmpTbsHis.objects.filter(tags=tagsdefault, pct_used__isnull=False).order_by('-chk_time')[0]

    tmpgrow = models_oracle.OracleTmpTbsHis.objects.filter(tags=tagsdefault, pct_used__isnull=False).filter(
        chk_time__gt=tmp_begin_time, chk_time__lt=end_time).order_by('-chk_time')
    tmpgrow_list = list(tmpgrow)
    tmpgrow_list.reverse()

    psgrow = models_oracle.OracleDbHis.objects.filter(tags=tagsdefault, qps__isnull=False).filter(
        chk_time__gt=ps_begin_time, chk_time__lt=end_time).order_by('-chk_time')
    psgrow_list = list(psgrow)
    psgrow_list.reverse()
    # 连接信息
    sql = "select host,port,service_name,user,password,user_os,password_os from tab_oracle_servers where tags= '%s' " % tagsdefault
    oracle = tools.mysql_query(sql)
    host = oracle[0][0]
    port = oracle[0][1]
    service_name = oracle[0][2]
    user = oracle[0][3]
    password = oracle[0][4]
    password = base64.decodestring(password)
    url = host + ':' + port + '/' + service_name

    if request.method == 'POST':
        if request.POST.has_key('select_tags') or request.POST.has_key('select_conn') or request.POST.has_key('select_undo') or request.POST.has_key('select_tmp') or request.POST.has_key('select_ps'):
            if request.POST.has_key('select_tags'):
                tagsdefault = request.POST.get('select_tags', None).encode("utf-8")
            elif request.POST.has_key('select_conn'):
                conn_range_default = request.POST.get('select_conn',None)
            elif request.POST.has_key('select_undo'):
                undo_range_default = request.POST.get('select_undo', None)
            elif request.POST.has_key('select_tmp'):
                tmp_range_default = request.POST.get('select_tmp', None)
            elif request.POST.has_key('select_ps'):
                ps_range_default = request.POST.get('select_ps', None)
            return HttpResponseRedirect('/oracle_monitor?tagsdefault=%s&conn_range_default=%s&undo_range_default=%s&tmp_range_default=%s&ps_range_default=%s' %(tagsdefault,conn_range_default,undo_range_default,tmp_range_default,ps_range_default))

        else:
            logout(request)
            return HttpResponseRedirect('/login/')

    if messageinfo_list:
        msg_num = len(messageinfo_list)
        msg_last = models_frame.TabAlarmInfo.objects.latest('id')
        msg_last_content = msg_last.alarm_content
        tim_last = (datetime.datetime.now() - msg_last.alarm_time).seconds / 60
    else:
        msg_num = 0
        msg_last_content = ''
        tim_last = ''
    return render_to_response('oracle_monitor.html',
                              {'conngrow_list': conngrow_list, 'undogrow_list': undogrow_list, 'tmpinfo': tmpinfo,
                               'tmpgrow_list': tmpgrow_list,'psgrow_list': psgrow_list, 'tagsdefault': tagsdefault, 'tagsinfo': tagsinfo,
                               'oracleinfo': oracleinfo, 'undoinfo': undoinfo, 'eventinfo': eventinfo,
                               'lockinfo': lockinfo, 'messageinfo_list': messageinfo_list,
                               'msg_num': msg_num, 'conn_range_default': conn_range_default,
                               'undo_range_default': undo_range_default, 'tmp_range_default': tmp_range_default,'ps_range_default': ps_range_default,
                               'msg_last_content': msg_last_content, 'tim_last': tim_last,'check_status':check_status,'oracle_status':oracle_status})

@login_required(login_url='/login')
def show_oracle(request):
    messageinfo_list = models_frame.TabAlarmInfo.objects.all()
    dbinfo_list = models_oracle.OracleDb.objects.order_by("rate_level")
    paginator = Paginator(dbinfo_list, 10)
    page = request.GET.get('page')
    try:
        dbinfos = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        dbinfos = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        dbinfos = paginator.page(paginator.num_pages)

    if request.method == 'POST':
        logout(request)
        return HttpResponseRedirect('/login/')

    if messageinfo_list:
        msg_num = len(messageinfo_list)
        msg_last = models_frame.TabAlarmInfo.objects.latest('id')
        msg_last_content = msg_last.alarm_content
        tim_last = (datetime.datetime.now() - msg_last.alarm_time).seconds / 60
    else:
        msg_num = 0
        msg_last_content = ''
        tim_last = ''
    return render_to_response('show_oracle.html',
                              {'dbinfos': dbinfos, 'messageinfo_list': messageinfo_list, 'msg_num': msg_num,
                               'msg_last_content': msg_last_content, 'tim_last': tim_last})


@login_required(login_url='/login')
def show_oracle_resource(request):
    messageinfo_list = models_frame.TabAlarmInfo.objects.all()
    tagsinfo = models_oracle.OracleDb.objects.filter(mon_status='connected')

    tagsdefault = request.GET.get('tagsdefault')
    if not tagsdefault:
        tagsdefault = models_oracle.OracleDb.objects.filter(mon_status='connected').order_by('tags')[0].tags
    typedefault = request.GET.get('typedefault')

    redo_range_default = request.GET.get('redo_range_default')
    if not redo_range_default:
        redo_range_default  = 7

    tbsinfo_list = models_oracle.OracleTbs.objects.filter(tags=tagsdefault).order_by('-pct_used')
    # 分页
    paginator_tbs = Paginator(tbsinfo_list, 5)
    undotbsinfo_list = models_oracle.OracleUndoTbs.objects.filter(tags=tagsdefault).order_by('-pct_used')
    paginator_undo = Paginator(undotbsinfo_list, 5)
    tmptbsinfo_list = models_oracle.OracleTmpTbs.objects.filter(tags=tagsdefault).order_by('-pct_used')
    paginator_tmp = Paginator(tmptbsinfo_list, 5)

    page_tbs = request.GET.get('page_tbs')
    try:
        tbsinfos = paginator_tbs.page(page_tbs)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        tbsinfos = paginator_tbs.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        tbsinfos = paginator_tbs.page(paginator_tbs.num_pages)
    page_undo = request.GET.get('page_undo')
    try:
        undotbsinfos = paginator_undo.page(page_undo)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        undotbsinfos = paginator_undo.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        undotbsinfos = paginator_undo.page(paginator_undo.num_pages)
    page_tmp = request.GET.get('page_tmp')
    try:
        tmptbsinfos = paginator_undo.page(page_tmp)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        tmptbsinfos = paginator_tmp.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        tmptbsinfos = paginator_tmp.page(paginator_tmp.num_pages)

    # 获取控制文件信息
    sql = "select host,port,service_name,user,password,user_os,password_os from tab_oracle_servers where tags= '%s' " % tagsdefault
    oracle = tools.mysql_query(sql)
    host = oracle[0][0]
    port = oracle[0][1]
    service_name = oracle[0][2]
    user = oracle[0][3]
    password = oracle[0][4]
    password = base64.decodestring(password)
    url = host + ':' + port + '/' + service_name
    sql = """
        select name,round(block_size*file_size_blks/1024/1024,2) size_M,'controlfile' tpye  from v$controlfile
          """
    oracle_controlfiles = tools.oracle_django_query(user, password, url, sql)
    # 获取在线日志
    sql = """
    select a.GROUP# group_no,b.THREAD# thread_no,a.TYPE,b.SEQUENCE# sequence_no,b.BYTES/1024/1024 SIZE_M,b.ARCHIVED,b.STATUS,a.MEMBER from v$logfile a,v$log b where a.GROUP#=b.GROUP#(+)
    """
    oracle_redo_files = tools.oracle_django_query(user, password, url, sql)
    # 在线日志统计
    if redo_range_default == '1':
        sql = """
        select  'hh'||to_char(first_time, 'hh24') stat_date,
            count(1) log_count,
            (select bytes / 1024 / 1024 sizem from v$log where rownum < 2) log_size
       from v$log_history
      where to_char(first_time, 'yyyymmdd') < to_char(sysdate, 'yyyymmdd')
        and to_char(first_time, 'yyyymmdd') >=
            to_char(sysdate - 1, 'yyyymmdd')
      group by to_char(first_time, 'hh24'),to_char(first_time, 'dy')
      order by to_char(first_time, 'hh24')
        """
        oracle_redo_cnts = tools.oracle_django_query(user, password, url, sql)
    else:
        sql = """ select to_char(first_time, 'yyyy-mm-dd') stat_date,
               count(1) log_count,
               (select bytes / 1024 / 1024 sizem from v$log where rownum < 2) log_size
          from v$log_history
         where to_char(first_time, 'yyyymmdd') < to_char(sysdate, 'yyyymmdd')
         and to_char(first_time, 'yyyymmdd') >= to_char(sysdate-%s, 'yyyymmdd')
         group by to_char(first_time, 'yyyy-mm-dd'), to_char(first_time, 'dy')  order by to_char(first_time, 'yyyy-mm-dd')""" % redo_range_default
        oracle_redo_cnts = tools.oracle_django_query(user, password, url, sql)
    # 表变化记录
    sql = """
        select table_owner,table_name,inss,upds,dels,
               to_char(inss + upds + dels) dmls,to_char(sysdate , 'yyyy-mm-dd') get_date,truncated,num_rows,
               to_char(last_analyzed  ,'yyyy-mm-dd hh24:mi:ss') last_analyzed
        from (select m.table_owner, m.table_name, inserts as inss, updates as upds, deletes as dels, truncated, t.num_rows,t.last_analyzed
            from sys.dba_tab_modifications m, dba_tables t
            where m.table_name = t.table_name
            and t.owner not in ('SYS','SYSTEM','OUTLN','DIP','ORACLE_OCM','DBSNMP','APPQOSSYS','WMSYS','EXFSYS',
            'CTXSYS','ANONYMOUS','XDB','XS$NULL','ORDDATA','SI_INFORMTN_SCHEMA','ORDPLUGINS','ORDSYS','MDSYS','OLAPSYS',
            'MDDATA','SPATIAL_WFS_ADMIN_USR','SPATIAL_CSW_ADMIN_USR','SYSMAN','MGMT_VIEW','APEX_030200','FLOWS_FILES',
            'APEX_PUBLIC_USER','OWBSYS','OWBSYS_AUDIT','SCOTT')
            and m.table_owner = t.owner and m.partition_name is null)
        """
    oracle_table_changes = tools.oracle_django_query(user, password, url, sql)
    # 序列
    sql = """
        select sequence_owner,sequence_name,min_value,max_value,increment_by,cycle_flag,order_flag,
               cache_size,last_number,
               round((max_value - last_number) / (max_value - min_value), 2) * 100 pct_used,
               (case when (round((max_value - last_number) / (max_value - min_value), 2) * 100) > 30 
                       then 'green'
                      when (round((max_value - last_number) / (max_value - min_value), 2) * 100) <= 30 and (round((max_value - last_number) / (max_value - min_value), 2) * 100) > 10
                       then 'yellow'
                      when (round((max_value - last_number) / (max_value - min_value), 2) * 100) <= 10
                      then 'red'
                      else ''
                     end) seq_color,
               to_char(sysdate, 'yyyy-mm-dd') last_analyzed
          from dba_sequences s
         where s.sequence_owner not in ('SYS','SYSTEM','OUTLN','DIP','ORACLE_OCM','DBSNMP','APPQOSSYS','WMSYS','EXFSYS',
        'CTXSYS','ANONYMOUS','XDB','XS$NULL','ORDDATA','SI_INFORMTN_SCHEMA','ORDPLUGINS','ORDSYS','MDSYS','OLAPSYS',
        'MDDATA','SPATIAL_WFS_ADMIN_USR','SPATIAL_CSW_ADMIN_USR','SYSMAN','MGMT_VIEW','APEX_030200','FLOWS_FILES',
        'APEX_PUBLIC_USER','OWBSYS','OWBSYS_AUDIT','SCOTT')
        """
    oracle_sequences = tools.oracle_django_query(user, password, url, sql)
    # 账号
    sql = """
        select username,profile,to_char(created,'yyyy-mm-dd hh24:mi:ss') created,
               account_status,
              (case when account_status <> 'OPEN' then 'red' else 'green'end ) account_color,
               to_char(lock_date,'yyyy-mm-dd hh24:mi:ss') lock_date,
               to_char(expiry_date,'yyyy-mm-dd hh24:mi:ss') expiry_date,
               (case when expiry_date - sysdate > 30 
                       then 'green'
                      when expiry_date - sysdate <= 30 and expiry_date - sysdate > 7 
                       then 'yellow'
                      when expiry_date - sysdate <= 7 
                      then 'red'
                      else ''
                     end) expiry_color,default_tablespace,temporary_tablespace
        from dba_users
        """
    oracle_users = tools.oracle_django_query(user, password, url, sql)

    # alert日志
    oracle_alert_logs = models_oracle.AlertLog.objects.filter(server_type='Oracle',tags=tagsdefault).order_by('-log_time')


    if request.method == 'POST':
        if request.POST.has_key('select_tags') :
            tagsdefault = request.POST.get('select_tags', None).encode("utf-8")
            return HttpResponseRedirect('/show_oracle_resource?tagsdefault=%s&redo_range_default=%s' %(tagsdefault,redo_range_default))
        else:
            logout(request)
            return HttpResponseRedirect('/login/')

    if messageinfo_list:
        msg_num = len(messageinfo_list)
        msg_last = models_frame.TabAlarmInfo.objects.latest('id')
        msg_last_content = msg_last.alarm_content
        tim_last = (datetime.datetime.now() - msg_last.alarm_time).seconds / 60
    else:
        msg_num = 0
        msg_last_content = ''
        tim_last = ''
    return render_to_response('show_oracle_res.html', {'tagsdefault': tagsdefault,'typedefault':typedefault,'tagsinfo': tagsinfo,'msg_num':msg_num,
                                                      'msg_last_content': msg_last_content, 'tim_last': tim_last,
                                                       'tbsinfos': tbsinfos, 'undotbsinfos': undotbsinfos,'tmptbsinfos': tmptbsinfos,'oracle_controlfiles':oracle_controlfiles,
                                                       'oracle_redo_files':oracle_redo_files,'oracle_redo_cnts':oracle_redo_cnts,'oracle_table_changes':oracle_table_changes,
                                                       'oracle_sequences':oracle_sequences,'oracle_users':oracle_users,'oracle_alert_logs':oracle_alert_logs})


@login_required(login_url='/login')
def oracle_profile(request):
    messageinfo_list = models_frame.TabAlarmInfo.objects.all()
    tags = request.GET.get('tags')
    profile_name = request.GET.get('profile_name')
    sql = "select host,port,service_name,user,password,user_os,password_os from tab_oracle_servers where tags= '%s' " %tags
    oracle = tools.mysql_query(sql)
    host = oracle[0][0]
    port = oracle[0][1]
    service_name = oracle[0][2]
    user = oracle[0][3]
    password = oracle[0][4]
    password = base64.decodestring(password)
    url = host + ':' + port + '/' + service_name
    sql = """
        select profile,resource_name,resource_type,limit,to_char(sysdate,'yyyy-mm-dd') get_date
          from dba_profiles where  profile = '%s'
        """ %profile_name

    oracle_profiles = tools.oracle_django_query(user,password,url,sql)

    now = tools.now()
    if request.method == 'POST':
        logout(request)
        return HttpResponseRedirect('/login/')

    if messageinfo_list:
        msg_num = len(messageinfo_list)
        msg_last = models_frame.TabAlarmInfo.objects.latest('id')
        msg_last_content = msg_last.alarm_content
        tim_last = (datetime.datetime.now() - msg_last.alarm_time).seconds / 60
    else:
        msg_num = 0
        msg_last_content = ''
        tim_last = ''
    return render_to_response('oracle_profile.html',
                              {'messageinfo_list': messageinfo_list,'msg_num':msg_num, 'oracle_profiles': oracle_profiles, 'profile_name':profile_name,'tags': tags,
                               'now': now,
                               'msg_last_content': msg_last_content, 'tim_last': tim_last})

@login_required(login_url='/login')
def oracle_grant(request):
    messageinfo_list = models_frame.TabAlarmInfo.objects.all()
    tags = request.GET.get('tags')
    username = request.GET.get('username')
    sql = "select host,port,service_name,user,password,user_os,password_os from tab_oracle_servers where tags= '%s' " %tags
    oracle = tools.mysql_query(sql)
    host = oracle[0][0]
    port = oracle[0][1]
    service_name = oracle[0][2]
    user = oracle[0][3]
    password = oracle[0][4]
    password = base64.decodestring(password)
    url = host + ':' + port + '/' + service_name
    # 角色权限
    sql = """
         select grantee,
         granted_role,
         admin_option,
         default_role,
         to_char(sysdate, 'yyyy-mm-dd') get_date
         from dba_role_privs where grantee = '%s'
        """ %username
    user_roles = tools.oracle_django_query(user,password,url,sql)
    # 系统权限
    sql = """
        select grantee,privilege,admin_option,to_char(sysdate,'yyyy-mm-dd') get_date
          from dba_sys_privs where grantee = '%s'
        """ %username
    sys_privs = tools.oracle_django_query(user,password,url,sql)
    # 对象权限
    sql = """
        select owner,grantee,grantor,table_name,privilege
               ,grantable,hierarchy,to_char(sysdate,'yyyy-mm-dd') get_date
          from dba_tab_privs
         where grantee <> 'PUBLIC' and privilege <> 'EXECUTE' and grantee = '%s'
        """ %username
    tab_privs = tools.oracle_django_query(user,password,url,sql)

    now = tools.now()
    if request.method == 'POST':
        logout(request)
        return HttpResponseRedirect('/login/')

    if messageinfo_list:
        msg_num = len(messageinfo_list)
        msg_last = models_frame.TabAlarmInfo.objects.latest('id')
        msg_last_content = msg_last.alarm_content
        tim_last = (datetime.datetime.now() - msg_last.alarm_time).seconds / 60
    else:
        msg_num = 0
        msg_last_content = ''
        tim_last = ''
    return render_to_response('oracle_grant.html',
                              {'messageinfo_list': messageinfo_list, 'msg_num':msg_num,'user_roles': user_roles,'sys_privs':sys_privs,
                               'tab_privs':tab_privs,'username':username,'tags': tags,'now': now,
                               'msg_last_content': msg_last_content, 'tim_last': tim_last})

@login_required(login_url='/login')
def show_oracle_rate(request):
    messageinfo_list = models_frame.TabAlarmInfo.objects.all()
    oracle_rate_list = models_oracle.OracleDbRate.objects.order_by("db_rate")
    if request.method == 'POST':
        logout(request)
        return HttpResponseRedirect('/login/')
    if messageinfo_list:
        msg_num = len(messageinfo_list)
        msg_last = models_frame.TabAlarmInfo.objects.latest('id')
        msg_last_content = msg_last.alarm_content
        tim_last = (datetime.datetime.now() - msg_last.alarm_time).seconds / 60
    else:
        msg_num = 0
        msg_last_content = ''
        tim_last = ''
    return render_to_response('show_oracle_rate.html',
                              {'oracle_rate_list': oracle_rate_list, 'messageinfo_list': messageinfo_list,
                               'msg_num': msg_num,
                               'msg_last_content': msg_last_content, 'tim_last': tim_last})



