#! /usr/bin/python
# encoding:utf-8
from django.shortcuts import render

# Create your views here.

from django.shortcuts import render

from django.shortcuts import render,render_to_response
from django.http import HttpResponse, HttpResponseRedirect

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# Create your views here.
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from django.http import HttpResponse
import datetime
import frame.models as models_frame
import redis_mon.models as models_redis
import frame.tools as tools
import frame.log_parse as logparser
from django.contrib import messages

@login_required(login_url='/login')
def redis_mon_conf_edit(request):
    status = 0
    rid = request.GET.get('id')
    redis_mon_conf_edit = models_redis.RedisMonConf.objects.get(id=rid)
    if request.method == "POST":
        if request.POST.has_key('commit'):
            tags = request.POST.get('tags', None)
            host = request.POST.get('host', None)
            port = request.POST.get('port', None)
            connect = request.POST.get('connect', None)
            connect = tools.isno(connect)
            mem = request.POST.get('mem', None)
            mem = tools.isno(mem)
            models_redis.RedisMonConf.objects.filter(id=rid).update(tags=tags,host=host,port=port,
                                                                 connect=connect, mem=mem)
            status = 1
        elif request.POST.has_key('logout'):
            logout(request)
            return HttpResponseRedirect('/login/')

    return render_to_response('redis_mon/redis_mon_edit.html', {'redis_mon_conf_edit': redis_mon_conf_edit, 'status':status})

@login_required(login_url='/login')
def redis_mon_conf_add(request):
    status = 0
    if request.method == "POST":
        if request.POST.has_key('commit'):
            tags = request.POST.get('tags', None)
            host = request.POST.get('host', None)
            port = request.POST.get('port', None)
            connect = request.POST.get('connect', None)
            connect = tools.isno(connect)
            mem = request.POST.get('mem', None)
            mem = tools.isno(mem)
            models_redis.RedisMonConf.objects.create(tags=tags, host=host, port=port,connect=connect, mem=mem )
            status = 1
        elif request.POST.has_key('logout'):
            logout(request)
            return HttpResponseRedirect('/login/')

    return render_to_response('redis_mon/redis_mon_add.html', {'status':status})

@login_required(login_url='/login')
def redis_mon_conf_del(request):
    rid = request.GET.get('id')
    models_redis.RedisMonConf.objects.filter(id=rid).delete()
    return HttpResponseRedirect('/mon_servers/')


@login_required(login_url='/login')
def show_redis(request):
    messageinfo_list = models_frame.TabAlarmInfo.objects.all()

    redis_list = models_redis.Redis.objects.all().order_by('mon_status')

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
    return render_to_response('redis_mon/show_redis.html',
                              {'redis_list': redis_list, 'messageinfo_list': messageinfo_list,
                               'msg_num': msg_num,
                               'msg_last_content': msg_last_content, 'tim_last': tim_last})


