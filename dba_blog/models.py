from __future__ import unicode_literals

from django.db import models

# Create your models here.

class BlogArticle(models.Model):
    created_time = models.DateTimeField()
    last_mod_time = models.DateTimeField()
    title = models.CharField(max_length=255)
    body = models.TextField(blank=True, null=True)
    pub_time = models.DateTimeField()
    status = models.CharField(max_length=255)
    comment_status = models.CharField(max_length=255)
    type = models.CharField(max_length=255)
    subtype = models.CharField(max_length=255)
    views = models.IntegerField(blank=True, null=True)
    article_order = models.IntegerField(blank=True, null=True)
    author_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'blog_article'


class BlogTag(models.Model):
    created_time = models.DateTimeField()
    last_mod_time = models.DateTimeField()
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'blog_tag'