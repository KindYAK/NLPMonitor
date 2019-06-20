from django.db import models
from mainapp.models import *


class TopicCorpus(models.Model):
    class Meta:
        verbose_name = "Корпус топиков"
        verbose_name_plural = "Корпусы топиков"
        unique_together = (('corpus', 'name'))

    corpus = models.ForeignKey('mainapp.Corpus', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    description = models.TextField()


class Topic(models.Model):
    class Meta:
        verbose_name = "Топик"
        verbose_name_plural = "Топики"

    topic_corpus = models.ForeignKey('TopicCorpus', on_delete=models.CASCADE)
    name = models.CharField(max_length=250, null=True, blank=True)
    topic_parent = models.ForeignKey('Topic', null=True, blank=True, on_delete=models.CASCADE)


class TopicUnit(models.Model):
    class Meta:
        verbose_name = "Единица-описание топика"
        verbose_name_plural = "Единицы-описания топика"
        # unique_together = (('topic', 'text'))

    topic = models.ForeignKey('Topic', on_delete=models.CASCADE)
    weight = models.FloatField(null=True, blank=True)
    text = models.CharField(max_length=100)


class DocumentTopic(models.Model):
    class Meta:
        verbose_name = "Связь документа и топика"
        verbose_name_plural = "Связи документов и топиков"
        # unique_together = (('topic', 'document'))

    topic = models.ForeignKey('Topic', on_delete=models.CASCADE)
    document = models.ForeignKey('mainapp.Document', on_delete=models.CASCADE)
    weight = models.FloatField(null=True, blank=True)
