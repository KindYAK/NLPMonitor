from django.db import models
from mainapp.models import *
from picklefield.fields import PickledObjectField


class ProcessedCorpus(models.Model):
    class Meta:
        verbose_name = "Обработанный корпус"
        verbose_name_plural = "Обработанные корпусы"
        unique_together = (('corpus', 'name'))
        indexes = [
            models.Index(fields=['corpus']),
        ]

    corpus = models.ForeignKey('mainapp.Corpus', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    description = models.TextField()


class ProcessedDocument(models.Model):
    class Meta:
        verbose_name = "Обработанный документ"
        verbose_name_plural = "Обработанные документы"
        unique_together = (('processed_corpus', 'original_document'))
        indexes = [
            models.Index(fields=['processed_corpus']),
            models.Index(fields=['original_document']),
        ]

    processed_corpus = models.ForeignKey('ProcessedCorpus', on_delete=models.CASCADE)
    original_document = models.ForeignKey('mainapp.Document', on_delete=models.CASCADE)


class AnalysisUnit(models.Model):
    class Meta:
        verbose_name = "Базовая единица анализа"
        verbose_name_plural = "Базовые единицы анализа"
        unique_together = (('processed_document', 'index', 'value'))
        indexes = [
            models.Index(fields=['processed_document']),
        ]

    UNIT_TYPES = (
        (0, "subword"),
        (1, "word"),
        (2, "n-gram/phrase"),
        (3, "sentence"),
        (4, "paragraph"),
        (5, "text"),
    )

    type = models.SmallIntegerField(choices=UNIT_TYPES)
    processed_document = models.ForeignKey('ProcessedDocument', on_delete=models.CASCADE)
    value = models.TextField()
    index = models.IntegerField(default=0)
    embedding = PickledObjectField(null=True, blank=True)
