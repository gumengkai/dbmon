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

@login_required(login_url='/login')
def show_linux(request):
    osinfo_list = models_linux.OsInfo.objects.all()
    paginator_os = Paginator(osinfo_list, 5)
    diskinfo_list = models_linux.OsFilesystem.objects.order_by("-pct_used")
    paginator_disk = Paginator(diskinfo_list, 5)
    page_os = request.GET.get('page_os')
    try:
        osinfos = paginator_os.page(page_os)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        osinfos = paginator_os.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        osinfos = paginator_os.page(paginator_os.num_pages)
    page_undo = request.GET.get('page_disk')
    try:
        diskinfos = paginator_disk.page(page_undo)
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
        return render_to_response('show_linux.html', {'osinfos': osinfos,'diskinfos':diskinfos, 'messageinfo_list': messageinfo_list,
                                                   'msg_num': msg_num,
                                                   'msg_last_content': msg_last_content, 'tim_last': tim_last})
    else:
        return render_to_response('show_linux.html', {'osinfos': osinfos, 'diskinfos': diskinfos})

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
        return render_to_response('show_linux_rate.html', {'linux_rate_list': linux_rate_list, 'messageinfo_list': messageinfo_list,
                                                   'msg_num': msg_num,
                                                   'msg_last_content': msg_last_content, 'tim_last': tim_last})
    else:
        return render_to_response('show_linux_rate.html', { 'linux_rate_list': linux_rate_list})


@login_required(login_url='/login')
def linux_monitor(request):
    messageinfo_list = models_frame.TabAlarmInfo.objects.all()
    tagsdefault = request.GET.get('tagsdefault')
    if not tagsdefault:
        tagsdefault = models_linux.TabLinuxServers.objects.order_by('tags')[0].tags
    load_range_defualt = request.GET.get('load_range_default')
    if not load_range_defualt:
        load_range_defualt = '1小时'.decode("utf-8")
    cpu_range_defualt =   request.GET.get('cpu_range_default')
    if not cpu_range_defualt:
        cpu_range_defualt = '1小时'.decode("utf-8")
    mem_range_default = request.GET.get('mem_range_default')
    if not mem_range_default:
        mem_range_default = '1小时'.decode("utf-8")
    net_range_default = request.GET.get('net_range_default')
    if not net_range_default:
        net_range_default = '1小时'.decode("utf-8")
    tcp_range_default = request.GET.get('tcp_range_default')
    if not tcp_range_default:
        tcp_range_default = '1小时'.decode("utf-8")
    hostinfo = models_linux.TabLinuxServers.objects.all().order_by('tags')



    net_begin_time = tools.range(net_range_default)
    cpu_begin_time = tools.range(cpu_range_defualt)
    mem_begin_time = tools.range(mem_range_default)
    tcp_begin_time = tools.range(tcp_range_default)
    end_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    netgrow = models_linux.OsInfoHis.objects.filter(tags=tagsdefault, recv_kbps__isnull=False).filter(
        chk_time__gt=net_begin_time, chk_time__lt=end_time).order_by('-chk_time')
    netgrow_list = list(netgrow)
    netgrow_list.reverse()

    loadgrow = models_linux.OsInfoHis.objects.filter(tags=tagsdefault, load1__isnull=False).filter(
        chk_time__gt=cpu_begin_time, chk_time__lt=end_time).order_by('-chk_time')
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
        if request.POST.has_key('select_tags') or request.POST.has_key('select_load') or request.POST.has_key('select_cpu') or request.POST.has_key('select_mem') or request.POST.has_key('select_net') or request.POST.has_key('select_tcp') :
            if request.POST.has_key('select_tags'):
                tagsdefault = request.POST.get('select_tags', None).encode("utf-8")
            elif request.POST.has_key('select_net'):
                net_range_default = request.POST.get('select_net',None)
            elif request.POST.has_key('select_load'):
                load_range_defualt = request.POST.get('select_load',None)
            elif request.POST.has_key('select_cpu'):
                cpu_range_defualt = request.POST.get('select_cpu',None)
            elif request.POST.has_key('select_mem'):
                mem_range_default = request.POST.get('select_mem', None)
            elif request.POST.has_key('select_tcp'):
                tcp_range_default = request.POST.get('select_tcp', None)
            return HttpResponseRedirect('/linux_monitor?tagsdefault=%s&net_range_default=%s&load_range_default=%s&cpu_range_default=%s&mem_range_default=%s&tcp_range_default=%s' %(tagsdefault,net_range_default,load_range_defualt,cpu_range_defualt,mem_range_default,tcp_range_default))
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
    return render_to_response('linux_monitor.html',
                              {'netgrow_list': netgrow_list, 'loadgrow_list': loadgrow_list,'cpugrow_list': cpugrow_list,
                               'memgrow_list': memgrow_list,'tcpgrow_list': tcpgrow_list,
                               'tagsdefault': tagsdefault, 'hostinfo': hostinfo, 'osinfo': osinfo,
                               'net_range_default': net_range_default,'load_range_default':load_range_defualt, 'cpu_range_default': cpu_range_defualt,
                               'mem_range_default': mem_range_default,'tcp_range_default': tcp_range_default, 'messageinfo_list': messageinfo_list,
                               'msg_num': msg_num, 'msg_last_content': msg_last_content, 'tim_last': tim_last,
                               'diskinfos': diskinfos,'check_status':check_status,'os_status':os_status})


def page_not_found(request):
    return render(request, '404.html')