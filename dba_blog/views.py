# encoding: utf-8

from django.shortcuts import render

# Create your views here.
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render,render_to_response,RequestContext
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import markdown

import datetime
import frame.models as models_frame
import dba_blog.models as models_blog
import frame.tools as tools

@login_required(login_url='/login')
def blog_index(request):
    # 告警
    messageinfo_list = models_frame.TabAlarmInfo.objects.all()

    type = request.GET.get('type')
    subtype = request.GET.get('subtype')
    search = request.GET.get('search')

    author_id = request.GET.get('author_id')
    blog_tags = models_blog.BlogTag.objects.all()
    blog_views = models_blog.BlogArticle.objects.order_by('-views')[:10]

    sql = """
    select a.id,
       date_format(a.created_time,'%%Y-%%m-%%d') created_time,
       a.title,
       a.body,
       a.pub_time,
       a.type,
       a.subtype,
       a.views,
       a.author_id,
       b.username
  from blog_article a
  left join accounts_bloguser b
    on a.author_id = b. id where if ('%s'='None',1=1,a.type='%s') and if ('%s'='None',1=1,a.author_id='%s')
     and if ('%s'='None',1=1,a.subtype='%s') and if ('%s'='None',1=1,a.title like '%%%s%%' )  order by a.id desc
""" %(type,type,author_id,author_id,subtype,subtype,search,search)

    blog_article_list = tools.mysql_django_query(sql)

    if blog_article_list:
        paginator = Paginator(blog_article_list, 10)

        page = request.GET.get('page')
        try:
            blog_articles = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            blog_articles = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            blog_articles = paginator.page(paginator.num_pages)
    else:
        blog_articles = {}


    now = tools.now()
    if request.method == 'POST':
        if request.POST.has_key('search'):
            search = request.POST.get('search', None)
            return HttpResponseRedirect('/blog_index?search=%s' %search)
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
    return render_to_response('my_blog/blog_index.html', {'messageinfo_list': messageinfo_list,
                                                        'msg_num': msg_num, 'now': now,
                                                        'msg_last_content': msg_last_content,
                                                        'tim_last': tim_last,'blog_articles':blog_articles,
                                                          'blog_tags':blog_tags,'blog_views':blog_views,'type':type,
                                                          'subtype':subtype,'search':search})

@login_required(login_url='/login')
def article_detail(request):
    # 告警
    article_id = request.GET.get('id')
    messageinfo_list = models_frame.TabAlarmInfo.objects.all()
    blog_tags = models_blog.BlogTag.objects.all()
    blog_views = models_blog.BlogArticle.objects.order_by('-views')[:10]

    sql = """
    select a.id,
       date_format(a.created_time,'%%Y-%%m-%%d') created_time,
       a.title,
       a.body,
       a.pub_time,
       a.type,
       a.subtype,
       a.views,
       a.author_id,
       b.username
  from blog_article a
  left join accounts_bloguser b
    on a.author_id = b. id
  where a.id= %s """ %article_id

    article_detail = tools.mysql_django_query(sql)

    sql = "update blog_article a set a.views = a.views+1 where id = %s " %article_id

    tools.mysql_exec(sql,'')

    now = tools.now()
    if request.method == 'POST':
        if request.POST.has_key('search'):
            search = request.POST.get('search', None)
            return HttpResponseRedirect('/blog_index?search=%s' %search)
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
    return render_to_response('my_blog/article_detail.html', {'messageinfo_list': messageinfo_list,
                                                        'msg_num': msg_num, 'now': now,
                                                        'msg_last_content': msg_last_content,
                                                        'tim_last': tim_last,'article_detail':article_detail,
                                                          'blog_tags':blog_tags,'blog_views':blog_views})

@login_required(login_url='/login')
def article_edit(request):
    # 告警
    article_id = request.GET.get('id')
    messageinfo_list = models_frame.TabAlarmInfo.objects.all()
    blog_tags = models_blog.BlogTag.objects.all()
    blog_views = models_blog.BlogArticle.objects.order_by('-views')[:10]
    author_id = 1

    sql = """
    select a.id,
       date_format(a.created_time,'%%Y-%%m-%%d') created_time,
       a.title,
       a.body,
       a.pub_time,
       a.type,
       a.subtype,
       a.views,
       a.author_id,
       b.username
  from blog_article a
  left join accounts_bloguser b
    on a.author_id = b. id
  where a.id= %s """ %article_id

    article_detail = tools.mysql_django_query(sql)

    now = tools.now()
    if request.method == 'POST':
        if request.POST.has_key('commit'):
            title = request.POST.get('title', None)
            body = request.POST.get('body', None)
            type = request.POST.get('type', None)
            subtype = request.POST.get('subtype', None)

            models_blog.BlogArticle.objects.filter(id=article_id).update(title=title, body=body, type=type, subtype=subtype,author_id=author_id)
            return HttpResponseRedirect('/blog_index/')
        elif request.POST.has_key('search'):
            search = request.POST.get('search', None)
            return HttpResponseRedirect('/blog_index?search=%s' % search)
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
    return render_to_response('my_blog/article_edit.html', {'messageinfo_list': messageinfo_list,
                                                        'msg_num': msg_num, 'now': now,
                                                        'msg_last_content': msg_last_content,
                                                        'tim_last': tim_last,'article_detail':article_detail,

                                                          'blog_tags':blog_tags,'blog_views':blog_views})
@login_required(login_url='/login')
def article_add(request):
    # 告警
    article_id = request.GET.get('id')
    messageinfo_list = models_frame.TabAlarmInfo.objects.all()
    blog_tags = models_blog.BlogTag.objects.all()
    blog_views = models_blog.BlogArticle.objects.order_by('-views')[:10]
    author_id = 1

    now = tools.now()
    if request.method == 'POST':
        if request.POST.has_key('commit'):
            title = request.POST.get('title', None)
            body = request.POST.get('body', None)
            type = request.POST.get('type', None)
            subtype = request.POST.get('subtype', None)

            created_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            models_blog.BlogArticle.objects.create(title=title, body=body, type=type, subtype=subtype,author_id=author_id, created_time=created_time,views=0)
            # models_blog.BlogArticle.objects.filter(id=article_id).update(title=title, body=body, type=type, subtype=subtype,author_id=author_id)

            return HttpResponseRedirect('/blog_index')
        elif request.POST.has_key('search'):
            search = request.POST.get('search', None)
            return HttpResponseRedirect('/blog_index?search=%s' % search)
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
    return render_to_response('my_blog/article_add.html', {'messageinfo_list': messageinfo_list,
                                                        'msg_num': msg_num, 'now': now,
                                                        'msg_last_content': msg_last_content,
                                                        'tim_last': tim_last,
                                                          'blog_tags':blog_tags,'blog_views':blog_views})


@login_required(login_url='/login')
def article_archive(request):
    # 告警
    messageinfo_list = models_frame.TabAlarmInfo.objects.all()

    type = request.GET.get('type')
    author_id = request.GET.get('author_id')

    blog_tags = models_blog.BlogTag.objects.all()

    blog_views = models_blog.BlogArticle.objects.order_by('-views')[:10]

    sql = """
    select a.id,
       date_format(a.created_time,'%%Y-%%m-%%d') created_time,
       date_format(a.created_time,'%%Y') created_year,
       date_format(a.created_time,'%%m') created_month,
       a.title,
       a.body,
       a.pub_time,
       a.type,
       a.subtype,
       a.views,
       a.author_id,
       b.username
  from blog_article a
  left join accounts_bloguser b
    on a.author_id = b. id where if ('%s'='None',1=1,a.type='%s') and if ('%s'='None',1=1,a.author_id='%s') order by a.id desc
""" %(type,type,author_id,author_id)

    blog_articles = tools.mysql_django_query(sql)

    now = tools.now()
    if request.method == 'POST':
        if request.POST.has_key('search'):
            search = request.POST.get('search', None)
            return HttpResponseRedirect('/blog_index?search=%s' % search)
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
    return render_to_response('my_blog/article_archive.html', {'messageinfo_list': messageinfo_list,
                                                        'msg_num': msg_num, 'now': now,
                                                        'msg_last_content': msg_last_content,
                                                        'tim_last': tim_last,'blog_articles':blog_articles,
                                                          'blog_tags':blog_tags,'blog_views':blog_views})

@login_required(login_url='/login')
def article_delete(request):
    rid = request.GET.get('id')
    models_blog.BlogArticle.objects.filter(id=rid).delete()
    return HttpResponseRedirect('/blog_index/')