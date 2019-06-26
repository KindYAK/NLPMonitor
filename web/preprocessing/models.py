from django.db import models
from mainapp.models import *
from picklefield.fields import PickledObjectField


class ProcessedCorpus(models.Model):
    class Meta:
        verbose_name = "Обработанный корпус"
        verbose_name_plural = "Обработанные корпусы"
        unique_together = (('corpus', 'name'), )
        indexes = [
            models.Index(fields=['corpus']),
        ]

    corpus = models.ForeignKey('mainapp.Corpus', on_delete=models.CASCADE, verbose_name="Корпус")
    name = models.CharField(max_length=50, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")

    def __str__(self):
        return self.name


class ProcessedDocument(models.Model):
    class Meta:
        verbose_name = "Обработанный документ"
        verbose_name_plural = "Обработанные документы"
        unique_together = (('processed_corpus', 'original_document'), )
        indexes = [
            models.Index(fields=['processed_corpus']),
            models.Index(fields=['original_document']),
        ]

    processed_corpus = models.ForeignKey('ProcessedCorpus', on_delete=models.CASCADE, verbose_name="Обработанный корпус")
    original_document = models.ForeignKey('mainapp.Document', on_delete=models.CASCADE, verbose_name="Оригинальный документ")

    def __str__(self):
        return f"Корпус: {self.processed_corpus}, Документ: {self.original_document}"


class AnalysisUnit(models.Model):
    class Meta:
        verbose_name = "Базовая единица анализа"
        verbose_name_plural = "Базовые единицы анализа"

    UNIT_TYPES = (
        (0, "subword"),
        (1, "word"),
        (2, "n-gram/phrase"),
        (3, "sentence"),
        (4, "paragraph"),
        (5, "text"),
    )

    type = models.SmallIntegerField(choices=UNIT_TYPES, verbose_name="Тип единицы анализа")
    processed_document = models.ForeignKey('ProcessedDocument', on_delete=models.CASCADE, verbose_name="Обработанный документ")
    value = models.TextField(verbose_name="Значение")
    index = models.IntegerField(default=0, verbose_name="Индекс/позиция")
    embedding = PickledObjectField(null=True, blank=True, verbose_name="Embedding/векторизация")

    def __str__(self):
        return f"{self.value} из {self.processed_document}"
