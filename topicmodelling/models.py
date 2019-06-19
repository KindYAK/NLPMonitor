from django.db import models
from mainapp.models import *


class TopicCorpus(models.Model):
    corpus = models.ForeignKey('mainapp.Corpus', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    description = models.TextField()


class Topic(models.Model):
    topic_corpus = models.ForeignKey('TopicCorpus', on_delete=models.CASCADE)
    name = models.CharField(max_length=250, null=True, blank=True)
    topic_parent = models.ForeignKey('Topic', null=True, blank=True, on_delete=models.CASCADE)


class TopicUnit(models.Model):
    topic = models.ForeignKey('Topic', on_delete=models.CASCADE)
    weight = models.FloatField(null=True, blank=True)
    text = models.CharField(max_length=100)


class DocumentTopic(models.Model):
    topic = models.ForeignKey('Topic', on_delete=models.CASCADE)
    document = models.ForeignKey('mainapp.Document', on_delete=models.CASCADE)
    weight = models.FloatField(null=True, blank=True)
