#! /usr/bin/python
# encoding:utf-8

from django.shortcuts import render,render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.core import serializers
# Create your views here.
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
import datetime,time
from datetime import timedelta
import json
from frame import tools
import  frame.models as models_frame
import linux_mon.models as models_linux
import re
import os

@login_required(login_url='/login')
def show_linux(request):
    osinfo_list = models_linux.OsInfo.objects.order_by("rate_level")
    diskinfo_list = models_linux.OsFilesystem.objects.order_by("-pct_used")
    paginator_disk = Paginator(diskinfo_list, 5)
    page_disk = request.GET.get('page_disk')
    try:
        diskinfos = paginator_disk.page(page_disk)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        diskinfos = paginator_disk.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        diskinfos = paginator_disk.page(paginator_disk.num_pages)
    messageinfo_list = models_frame.TabAlarmInfo.objects.all()

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
    return render_to_response('linux_mon/show_linux.html', {'diskinfos': diskinfos, 'messageinfo_list': messageinfo_list,
                                                  'msg_num': msg_num,'osinfo_list':osinfo_list,
                                                  'msg_last_content': msg_last_content, 'tim_last': tim_last})



@login_required(login_url='/login')
def first(request):
    osinfo_host = models_linux.OsInfo.objects.get(host='192.168.48.10')
    return render_to_response('first.html',{'osinfo_host':osinfo_host})

@login_required(login_url='/login')
def show_linux_rate(request):
    messageinfo_list = models_frame.TabAlarmInfo.objects.all()
    linux_rate_list = models_linux.LinuxRate.objects.order_by("linux_rate")
    if request.method == 'POST':
        logout(request)
        return HttpResponseRedirect('/login/')
    if messageinfo_list:
        msg_num = len(messageinfo_list)
        msg_last = models_frame.TabAlarmInfo.objects.latest('id')
        msg_last_content = msg_last.alarm_content
        tim_last = (datetime.datetime.now() - msg_last.alarm_time).seconds / 60
        return render_to_response('linux_mon/show_linux_rate.html', {'linux_rate_list': linux_rate_list, 'messageinfo_list': messageinfo_list,
                                                   'msg_num': msg_num,
                                                   'msg_last_content': msg_last_content, 'tim_last': tim_last})
    else:
        return render_to_response('linux_mon/show_linux_rate.html', {'linux_rate_list': linux_rate_list})


@login_required(login_url='/login')
def linux_monitor(request):
    messageinfo_list = models_frame.TabAlarmInfo.objects.all()
    tagsdefault = request.GET.get('tagsdefault')
    if not tagsdefault:
        tagsdefault = models_linux.TabLinuxServers.objects.order_by('tags')[0].tags
    load_range_default = request.GET.get('load_range_default')
    if not load_range_default:
        load_range_default = '1小时'.decode("utf-8")
    cpu_range_default =   request.GET.get('cpu_range_default')
    if not cpu_range_default:
        cpu_range_default = '1小时'.decode("utf-8")
    mem_range_default = request.GET.get('mem_range_default')
    if not mem_range_default:
        mem_range_default = '1小时'.decode("utf-8")
    net_range_default = request.GET.get('net_range_default')
    if not net_range_default:
        net_range_default = '1小时'.decode("utf-8")
    tcp_range_default = request.GET.get('tcp_range_default')
    if not tcp_range_default:
        tcp_range_default = '1小时'.decode("utf-8")
    iops_range_default = request.GET.get('iops_range_default')
    if not iops_range_default:
        iops_range_default = '1小时'.decode("utf-8")

    iomb_range_default = request.GET.get('iomb_range_default')
    if not iomb_range_default:
        iomb_range_default = '1小时'.decode("utf-8")

    hostinfo = models_linux.TabLinuxServers.objects.all().order_by('tags')


    load_begin_time = tools.range(load_range_default)
    net_begin_time = tools.range(net_range_default)
    cpu_begin_time = tools.range(cpu_range_default)
    mem_begin_time = tools.range(mem_range_default)
    tcp_begin_time = tools.range(tcp_range_default)
    iops_begin_time = tools.range(iops_range_default)
    iomb_begin_time = tools.range(iomb_range_default)

    end_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    netgrow = models_linux.OsInfoHis.objects.filter(tags=tagsdefault, recv_kbps__isnull=False).filter(
        chk_time__gt=net_begin_time, chk_time__lt=end_time).order_by('-chk_time')
    netgrow_list = list(netgrow)
    netgrow_list.reverse()

    loadgrow = models_linux.OsInfoHis.objects.filter(tags=tagsdefault, load1__isnull=False).filter(
        chk_time__gt=load_begin_time, chk_time__lt=end_time).order_by('-chk_time')
    loadgrow_list = list(loadgrow)
    loadgrow_list.reverse()

    cpugrow = models_linux.OsInfoHis.objects.filter(tags=tagsdefault, cpu_used__isnull=False).filter(
        chk_time__gt=cpu_begin_time, chk_time__lt=end_time).order_by('-chk_time')
    cpugrow_list = list(cpugrow)
    cpugrow_list.reverse()

    memgrow = models_linux.OsInfoHis.objects.filter(tags=tagsdefault, mem_used__isnull=False).filter(
        chk_time__gt=mem_begin_time, chk_time__lt=end_time).order_by('-chk_time')
    memgrow_list = list(memgrow)
    memgrow_list.reverse()

    tcpgrow = models_linux.OsInfoHis.objects.filter(tags=tagsdefault, tcp_connected__isnull=False).filter(
        chk_time__gt=tcp_begin_time, chk_time__lt=end_time).order_by('-chk_time')
    tcpgrow_list = list(tcpgrow)
    tcpgrow_list.reverse()

    iopsgrow = models_linux.OsInfoHis.objects.filter(tags=tagsdefault, iops__isnull=False).filter(
        chk_time__gt=iops_begin_time, chk_time__lt=end_time).order_by('-chk_time')
    iopsgrow_list = list(iopsgrow)
    iopsgrow_list.reverse()

    iombgrow = models_linux.OsInfoHis.objects.filter(tags=tagsdefault, read_mb__isnull=False).filter(
        chk_time__gt=iomb_begin_time, chk_time__lt=end_time).order_by('-chk_time')
    iombgrow_list = list(iombgrow)
    iombgrow_list.reverse()


    diskinfos = models_linux.OsFilesystem.objects.filter(tags=tagsdefault)
    # 取当前主机状态
    try:
        os_curr = models_linux.OsInfo.objects.filter(tags=tagsdefault).get(tags=tagsdefault)
    except models_linux.OsInfo.DoesNotExist:
        os_curr = \
            models_linux.OsInfoHis.objects.filter(tags=tagsdefault).order_by('-chk_time')[0]

    try:
        try:
            osinfo = models_linux.OsInfo.objects.filter(tags=tagsdefault, cpu_used__isnull=False).get(tags=tagsdefault)
        except models_linux.OsInfo.DoesNotExist:
            osinfo = \
            models_linux.OsInfoHis.objects.filter(tags=tagsdefault, cpu_used__isnull=False).order_by('-chk_time')[0]
    except Exception,e:
        osinfo = \
            models_linux.OsInfoHis.objects.filter(tags=tagsdefault).order_by('-chk_time')[0]

    if os_curr.mon_status == 'connected':
        check_status = 'success'
        os_status = '在线'
    else:
        check_status = 'danger'
        os_status = '离线'

    if request.method == 'POST':
        if request.POST.has_key('select_tags') or request.POST.has_key('select_load') or request.POST.has_key('select_cpu') or request.POST.has_key('select_mem') or request.POST.has_key('select_net') or request.POST.has_key('select_tcp') or request.POST.has_key('select_iops') or request.POST.has_key('select_iomb') :
            if request.POST.has_key('select_tags'):
                tagsdefault = request.POST.get('select_tags', None).encode("utf-8")
            elif request.POST.has_key('select_net'):
                net_range_default = request.POST.get('select_net',None)
            elif request.POST.has_key('select_load'):
                load_range_default = request.POST.get('select_load',None)
            elif request.POST.has_key('select_cpu'):
                cpu_range_default = request.POST.get('select_cpu',None)
            elif request.POST.has_key('select_mem'):
                mem_range_default = request.POST.get('select_mem', None)
            elif request.POST.has_key('select_tcp'):
                tcp_range_default = request.POST.get('select_tcp', None)
            elif request.POST.has_key('select_iops'):
                iops_range_default = request.POST.get('select_iops', None)
            elif request.POST.has_key('select_iomb'):
                iomb_range_default = request.POST.get('select_iomb', None)
            return HttpResponseRedirect('/linux_monitor?tagsdefault=%s&net_range_default=%s&load_range_default=%s&cpu_range_default=%s&mem_range_default=%s&tcp_range_default=%s&iops_range_default=%s&iomb_range_default=%s' %(tagsdefault,net_range_default,load_range_default,cpu_range_default,mem_range_default,tcp_range_default,iops_range_default,iomb_range_default))
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
    return render_to_response('linux_mon/linux_monitor.html',
                              {'netgrow_list': netgrow_list, 'loadgrow_list': loadgrow_list,'cpugrow_list': cpugrow_list,
                               'memgrow_list': memgrow_list,'tcpgrow_list': tcpgrow_list,'iopsgrow_list':iopsgrow_list,'iops_range_default':iops_range_default,'iomb_range_default':iomb_range_default,
                               'tagsdefault': tagsdefault, 'hostinfo': hostinfo, 'osinfo': osinfo,'iombgrow_list':iombgrow_list,
                               'net_range_default': net_range_default,'load_range_default':load_range_default, 'cpu_range_default': cpu_range_default,
                               'mem_range_default': mem_range_default,'tcp_range_default': tcp_range_default, 'messageinfo_list': messageinfo_list,
                               'msg_num': msg_num, 'msg_last_content': msg_last_content, 'tim_last': tim_last,
                               'diskinfos': diskinfos,'check_status':check_status,'os_status':os_status})


@login_required(login_url='/login')
def show_linux_res(request):
    messageinfo_list = models_frame.TabAlarmInfo.objects.all()
    tagsinfo = models_linux.TabLinuxServers.objects.all()
    # 默认主机标签
    tagsdefault = request.GET.get('tagsdefault')
    if not tagsdefault:
        tagsdefault = models_linux.TabLinuxServers.objects.order_by('tags')[0].tags

     # 时间区间
    linux_range_default = request.GET.get('linux_range_default')
    if not linux_range_default:
        linux_range_default  = '1小时'

    # 磁盘选择
    diskinfo = models_linux.LinuxIoStat.objects.filter(tags=tagsdefault,disk__isnull=False)

    select_disk = request.GET.get('select_disk')
    if select_disk:
        select_disk = re.sub('\d+$', '', os.path.basename(select_disk))

    if not select_disk:
        select_disk = models_linux.LinuxIoStat.objects.filter(tags=tagsdefault,disk__isnull=False)[0].disk

    # 磁盘使用信息
    diskinfo_list = models_linux.OsFilesystem.objects.filter(tags=tagsdefault).order_by('-pct_used')

    linux_begin_time = tools.range(linux_range_default)
    end_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    disk_grow = models_linux.LinuxIoStatHis.objects.filter(tags=tagsdefault, disk=select_disk).filter(
        chk_time__gt=linux_begin_time, chk_time__lt=end_time).order_by('-chk_time')
    disk_grow_list = list(disk_grow)
    disk_grow_list.reverse()

    # 主机信息
    linux_begin_time = tools.range(linux_range_default)
    end_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    linux_grow = models_linux.OsInfoHis.objects.filter(tags=tagsdefault,updays__isnull=False).filter(
        chk_time__gt=linux_begin_time, chk_time__lt=end_time).order_by('-chk_time')
    linux_grow_list = list(linux_grow)
    linux_grow_list.reverse()

    if request.method == 'POST':
        if request.POST.has_key('select_tags') :
            tagsdefault = request.POST.get('select_tags', None).encode("utf-8")
            return HttpResponseRedirect('/show_linux_res?tagsdefault=%s' %(tagsdefault))
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
    return render_to_response('linux_mon/show_linux_res.html', {'tagsdefault': tagsdefault, 'tagsinfo': tagsinfo, 'msg_num':msg_num,
                                                      'msg_last_content': msg_last_content, 'tim_last': tim_last,'diskinfo':diskinfo,'select_disk':select_disk,
                                                       'diskinfo_list': diskinfo_list,'disk_grow_list':disk_grow_list,'linux_grow_list':linux_grow_list})



def page_not_found(request):
    return render(request, '404.html')