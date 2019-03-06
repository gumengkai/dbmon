#!/usr/bin/env python
# encoding: utf-8


"""
@version: ??
@author: liangliangyy
@license: MIT Licence
@contact: liangliangyy@gmail.com
@site: https://www.lylinux.net/
@software: PyCharm
@file: blog_tags.py
@time: 2016/11/2 下午11:10
"""

from django import template
from django.db.models import Q
from django.conf import settings
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe
import random
from django.utils.encoding import force_text
from django.shortcuts import get_object_or_404
import hashlib
import urllib
import logging

logger = logging.getLogger(__name__)

register = template.Library()

@register.filter(is_safe=True)
@stringfilter
def custom_markdown(content):
    from dbmon.utils import CommonMarkdown
    return mark_safe(CommonMarkdown.get_markdown(content))

@register.filter(is_safe=True)
@stringfilter
def truncatechars_content(content):
    """
    获得文章内容的摘要
    :param content:
    :return:
    """
    from django.template.defaultfilters import truncatechars_html
    return truncatechars_html(content, 100)

@register.simple_tag
def datetimeformat(data):
    try:
        return data.strftime(settings.DATE_TIME_FORMAT)
    except Exception as e:
        logger.error(e)
        return ""
