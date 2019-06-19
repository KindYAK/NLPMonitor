from django.db import models
from topicmodelling.models import Topic, DocumentTopic


class Corpus(models.Model):
    name = models.CharField(max_length=50)


class Source(models.Model):
    name = models.CharField(max_length=50)
    url = models.CharField(max_length=150, null=True, blank=True)
    corpus = models.ForeignKey('Corpus', on_delete=models.CASCADE)


class Author(models.Model):
    name = models.CharField(max_length=200)
    source = models.ForeignKey('Source', null=True, blank=True, on_delete=models.CASCADE)


class Document(models.Model):
    title = models.CharField(max_length=2500)
    author = models.ForeignKey('Author', null=True, blank=True, on_delete=models.CASCADE)
    text = models.TextField()
    html = models.TextField(null=True, blank=True)
    url = models.CharField(max_length=1000, null=True, blank=True)

    datetime = models.DateTimeField(null=True, blank=True)
    datetime_created = models.DateTimeField(auto_now_add=True)

    num_views = models.IntegerField(null=True, blank=True)
    num_shares = models.IntegerField(null=True, blank=True)
    num_comments = models.IntegerField(null=True, blank=True)
    num_likes = models.IntegerField(null=True, blank=True)

    tags = models.ManyToManyField('Tag')
    categories = models.ManyToManyField('Category')

    topics = models.ManyToManyField('topicmodelling.Topic', through='topicmodelling.DocumentTopic')


class Tag(models.Model):
    name = models.CharField(max_length=50)


class Category(models.Model):
    name = models.CharField(max_length=50)


class Comment(models.Model):
    text = models.TextField()
    document = models.ForeignKey('Document', null=True, blank=True, on_delete=models.CASCADE)
    datetime = models.DateTimeField(null=True, blank=True)
    datetime_created = models.DateTimeField(auto_now_add=True)
    reply_to = models.ForeignKey('Comment', null=True, blank=True, on_delete=models.CASCADE)
