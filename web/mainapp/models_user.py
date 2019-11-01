from django.contrib.auth.models import User
from django.db import models


class TopicGroup(models.Model):
    class Meta:
        verbose_name = "Группа топиков"
        verbose_name_plural = "Группы топиков"
        unique_together = (('name', 'owner'), )

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
