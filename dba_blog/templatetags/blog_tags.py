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
import markdown2

logger = logging.getLogger(__name__)

register = template.Library()

@register.filter(is_safe=True)
@stringfilter
def custom_markdown(value):
   return mark_safe(markdown2.markdown(force_text(value),
          extras=["fenced-code-blocks", "cuddled-lists", "metadata", "tables", "spoiler"]))
