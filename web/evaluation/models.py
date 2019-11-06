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
    value_range_from = models.SmallIntegerField(default=0)
    value_range_to = models.SmallIntegerField(default=1)
    is_integer = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class TopicsEval(models.Model):
    class Meta:
        verbose_name = "Оценка топика (группы топиков)"
        verbose_name_plural = "Оценки топика (группы топиков)"

    criterion = models.ForeignKey('EvalCriterion', on_delete=models.CASCADE)
    value = models.FloatField()
    topics = models.ManyToManyField('mainapp.TopicID', through='TopicIDEval', through_fields=('topics_eval', 'topic_id'))

    def __str__(self):
        return f"{self.criterion} - {self.value}"


class TopicIDEval(models.Model):
    class Meta:
        verbose_name = "Связь оценки и топика"
        verbose_name_plural = "Связи оценок и топиков"

    topic_id = models.ForeignKey('mainapp.TopicID', on_delete=models.CASCADE)
    topics_eval = models.ForeignKey('TopicsEval', on_delete=models.CASCADE)
    topic_modelling_name = models.CharField(max_length=100, verbose_name="Название ТМ")
    weight = models.FloatField()

    def __str__(self):
        return f"{self.topic_id} - {self.topics_eval}"


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
