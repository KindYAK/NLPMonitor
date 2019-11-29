from django.contrib.auth.models import User
from django.db import models
from picklefield import PickledObjectField


class ContentLoader(models.Model):
    class Meta:
        verbose_name = "Загрузчик контента"
        verbose_name_plural = "Загрузчики контента"

    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    corpus = models.ForeignKey('mainapp.Corpus', on_delete=models.CASCADE, verbose_name="Корпус")
    supervisor = models.BooleanField(default=False, verbose_name="Супервайзер")

    def __str__(self):
        return f"Загрузчик {self.user}"


class Expert(models.Model):
    class Meta:
        verbose_name = "Эксперт"
        verbose_name_plural = "Эксперты"

    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    topic_modelling_names = PickledObjectField(null=True, verbose_name="Название тематических моделирований")
    criterions = models.ManyToManyField('evaluation.EvalCriterion')

    def __str__(self):
        return f"Эксперт {self.user}"


class Viewer(models.Model):
    class Meta:
        verbose_name = "Пользователь (Viewer)"
        verbose_name_plural = "Пользователь (Viewer)"

    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    topic_modelling_names = PickledObjectField(null=True, verbose_name="Название тематических моделирований")
    criterions = models.ManyToManyField('evaluation.EvalCriterion')

    def __str__(self):
        return f"Пользователь {self.user}"


class TopicGroup(models.Model):
    class Meta:
        verbose_name = "Группа топиков"
        verbose_name_plural = "Группы топиков"
        unique_together = (('name', 'owner', 'topic_modelling_name'), )

    name = models.CharField(max_length=50, verbose_name="Название группы")
    topic_modelling_name = models.CharField(max_length=100, verbose_name="Название ТМ")
    topics = models.ManyToManyField('TopicID')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Владелец")
    is_public = models.BooleanField(default=False, verbose_name="Публичная группа")

    @property
    def size(self):
        return self.topics.objects.count()

    def __str__(self):
        return f"{self.name} из {self.topic_modelling_name}"


class TopicID(models.Model):
    class Meta:
        verbose_name = "ID Топика"
        verbose_name_plural = "ID топиков"
        unique_together = (('topic_modelling_name', 'topic_id'), )

    topic_modelling_name = models.CharField(max_length=100, verbose_name="Название ТМ")
    topic_id = models.CharField(max_length=50, verbose_name="ID топика")

    def __str__(self):
        return f"{self.topic_id} из {self.topic_modelling_name}"
