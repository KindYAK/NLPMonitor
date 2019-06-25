from django.db import models
from mainapp.models import Corpus


class EvalCorpus(models.Model):
    class Meta:
        verbose_name = "Корпус оценок"
        verbose_name_plural = "Корпусы оценок"
        unique_together = (('corpus', 'name'), )

    corpus = models.ForeignKey('mainapp.Corpus', on_delete=models.CASCADE)
    name = models.CharField(max_length=25)

    def __str__(self):
        return self.name


class EvalCriterion(models.Model):
    class Meta:
        verbose_name = "Критерий оценки"
        verbose_name_plural = "Критерии оценки"

    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class DocumentEval(models.Model):
    class Meta:
        verbose_name = "Оценка документа"
        verbose_name_plural = "Оценки документов"
        unique_together = (('corpus', 'document', 'evaluation_criterion'), )

    corpus = models.ForeignKey('EvalCorpus', on_delete=models.CASCADE)
    document = models.ForeignKey('mainapp.Document', on_delete=models.CASCADE)
    evaluation_criterion = models.ForeignKey('EvalCriterion', on_delete=models.CASCADE)
    value = models.FloatField()

    def __str__(self):
        return f"Оценка документа {self.document} по критерию {self.evaluation_criterion} - {self.value}"
