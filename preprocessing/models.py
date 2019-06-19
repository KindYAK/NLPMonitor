from django.db import models
from mainapp.models import *
from picklefield.fields import PickledObjectField


class ProcessedCorpus(models.Model):
    corpus = models.ForeignKey('mainapp.Corpus', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    description = models.TextField()


class ProcessedDocument(models.Model):
    processed_corpus = models.ForeignKey('ProcessedCorpus', on_delete=models.CASCADE)
    original_document = models.ForeignKey('mainapp.Document', on_delete=models.CASCADE)


class AnalysisUnit(models.Model):
    UNIT_TYPES = (
        (0, "subword"),
        (1, "word"),
        (2, "n-gram/phrase"),
        (3, "sentence"),
        (4, "paragraph"),
        (5, "text"),
    )

    processed_document = models.ForeignKey('ProcessedDocument', on_delete=models.CASCADE)
    type = models.SmallIntegerField(choices=UNIT_TYPES)
    embedding = PickledObjectField(null=True, blank=True)
