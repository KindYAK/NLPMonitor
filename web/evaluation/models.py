from django.contrib.auth.models import User
from django.db import models
from mainapp.models import Corpus


class EvalCriterion(models.Model):
    class Meta:
        verbose_name = "Критерий оценки"
        verbose_name_plural = "Критерии оценки"

    name = models.CharField(max_length=50, unique=True)
    value_range_from = models.SmallIntegerField(default=0)
    value_range_to = models.SmallIntegerField(default=1)
    is_integer = models.BooleanField(default=False)
    is_categorical = models.BooleanField(default=False)
    calc_virt_negative = models.BooleanField(default=False)
    group = models.ForeignKey('EvalCriterionGroup', null=True, blank=True, on_delete=models.CASCADE, related_name="criterions")

    def __str__(self):
        return self.name


class EvalCriterionGroup(models.Model):
    class Meta:
        verbose_name = "Группа критериев оценки"
        verbose_name_plural = "Группы критериев оценки"

    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class CategoricalCriterionValue(models.Model):
    class Meta:
        verbose_name = "Катеогриальное значение критерия"
        verbose_name_plural = "Категориальные значения критериев"
        unique_together = (('criterion', 'char_value'), ('criterion', 'int_value'), ('int_value', 'char_value'))

    criterion = models.ForeignKey('EvalCriterion', on_delete=models.CASCADE, related_name='cat_values')
    int_value = models.SmallIntegerField()
    char_value = models.CharField(max_length=100)


class TopicsEval(models.Model):
    class Meta:
        verbose_name = "Оценка топика (группы топиков)"
        verbose_name_plural = "Оценки топика (группы топиков)"

    criterion = models.ForeignKey('EvalCriterion', on_delete=models.CASCADE)
    topics = models.ManyToManyField('mainapp.TopicID', through='TopicIDEval', through_fields=('topics_eval', 'topic_id'))
    value = models.FloatField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"{self.criterion} - {self.value}"


class TopicIDEval(models.Model):
    class Meta:
        verbose_name = "Связь оценки и топика"
        verbose_name_plural = "Связи оценок и топиков"
        unique_together = (('topic_id', 'topics_eval'),)

    topic_id = models.ForeignKey('mainapp.TopicID', on_delete=models.CASCADE)
    topics_eval = models.ForeignKey('TopicsEval', on_delete=models.CASCADE)
    weight = models.FloatField()

    def __str__(self):
        return f"{self.topic_id} - {self.topics_eval}"


# !!!!!!!!!!!!! POTENTIALLY DEPRICATED !!!!!!!!!!!!!!
class EvalCorpus(models.Model):
    class Meta:
        verbose_name = "OLD? Корпус оценок"
        verbose_name_plural = "OLD? Корпусы оценок"
        unique_together = (('corpus', 'name'), )

    corpus = models.ForeignKey('mainapp.Corpus', on_delete=models.CASCADE)
    name = models.CharField(max_length=25)

    def __str__(self):
        return self.name


class DocumentEval(models.Model):
    class Meta:
        verbose_name = "OLD? Оценка документа"
        verbose_name_plural = "OLD? Оценки документов"
        unique_together = (('corpus', 'document', 'evaluation_criterion'), )

    corpus = models.ForeignKey('EvalCorpus', on_delete=models.CASCADE)
    document = models.ForeignKey('mainapp.Document', on_delete=models.CASCADE)
    evaluation_criterion = models.ForeignKey('EvalCriterion', on_delete=models.CASCADE)
    value = models.FloatField()

    def __str__(self):
        return f"Оценка документа {self.document} по критерию {self.evaluation_criterion} - {self.value}"
