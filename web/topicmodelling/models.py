from django.db import models
from mainapp.models import *


class TopicCorpus(models.Model):
    class Meta:
        verbose_name = "Корпус топиков"
        verbose_name_plural = "Корпусы топиков"
        unique_together = (('corpus', 'name'), )

    corpus = models.ForeignKey('mainapp.Corpus', on_delete=models.CASCADE, verbose_name="Корпус")
    name = models.CharField(max_length=50, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")

    def __str__(self):
        return self.name


class Topic(models.Model):
    class Meta:
        verbose_name = "Топик"
        verbose_name_plural = "Топики"

    topic_corpus = models.ForeignKey('TopicCorpus', on_delete=models.CASCADE, verbose_name="Корпус топиков")
    name = models.CharField(max_length=250, null=True, blank=True, verbose_name="Название")
    topic_parent = models.ForeignKey('Topic', null=True, blank=True, on_delete=models.CASCADE, verbose_name="Родительский топик")

    def __str__(self):
        return self.name


class TopicUnit(models.Model):
    class Meta:
        verbose_name = "Единица-описание топика"
        verbose_name_plural = "Единицы-описания топика"

    topic = models.ForeignKey('Topic', on_delete=models.CASCADE, verbose_name="Топик")
    weight = models.FloatField(null=True, blank=True, verbose_name="Вес")
    text = models.CharField(max_length=100, verbose_name="Текст")
    unique_hash = models.CharField(max_length=32, null=True, blank=True, unique=True, verbose_name="Уникальность topic, text")

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        hash = hashlib.md5()
        hash.update(str(self.topic.id).encode())
        hash.update(self.text.encode())
        self.unique_hash = hash.hexdigest()
        super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return self.text


class DocumentTopic(models.Model):
    class Meta:
        verbose_name = "Связь документа и топика"
        verbose_name_plural = "Связи документов и топиков"
        unique_together = (('topic', 'document'), )

    topic = models.ForeignKey('Topic', on_delete=models.CASCADE, verbose_name="Топик")
    document = models.ForeignKey('mainapp.Document', on_delete=models.CASCADE, verbose_name="Документ")
    weight = models.FloatField(null=True, blank=True, verbose_name="Вес")

    def __str__(self):
        return f"Топик {self.topic}, Документ {self.document}"
