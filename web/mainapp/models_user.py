from django.contrib.auth.models import User
from django.db import models


class UserGroup(models.Model):
    class Meta:
        verbose_name = "Группа пользователей"
        verbose_name_plural = "Группы пользователей"

    name = models.CharField(max_length=50, unique=True)
    corpuses = models.ManyToManyField('mainapp.Corpus', blank=True, verbose_name="Корпусы")
    topic_modelling_names = models.TextField(null=True, blank=True, verbose_name="Названия тематических моделирований (через запятую без пробелов)")
    criterions = models.ManyToManyField('evaluation.EvalCriterion', blank=True)
    dashboard_presets = models.ManyToManyField('dashboard.DashboardPreset', blank=True)

    def __str__(self):
        return f"Группа {self.name}"


class ContentLoader(models.Model):
    class Meta:
        verbose_name = "Загрузчик контента"
        verbose_name_plural = "Загрузчики контента"

    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    group = models.ForeignKey('UserGroup', on_delete=models.CASCADE, null=True)
    supervisor = models.BooleanField(default=False, verbose_name="Супервайзер")

    def __str__(self):
        return f"Загрузчик {self.user}"


class Expert(models.Model):
    class Meta:
        verbose_name = "Эксперт"
        verbose_name_plural = "Эксперты"

    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    group = models.ForeignKey('UserGroup', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"Эксперт {self.user}"


class Viewer(models.Model):
    class Meta:
        verbose_name = "Пользователь (Viewer)"
        verbose_name_plural = "Пользователь (Viewer)"

    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    group = models.ForeignKey('UserGroup', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"Пользователь {self.user}"


class TopicGroup(models.Model):
    class Meta:
        verbose_name = "Группа топиков"
        verbose_name_plural = "Группы топиков"
        unique_together = (('name', 'owner', 'topic_modelling_name'), )

    name = models.CharField(max_length=100, verbose_name="Название группы")
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


class Subscription(models.Model):
    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        unique_together = (('user', 'criterion', 'topic_modelling_name', 'subscription_type'), )

    TYPES = (
        (-1, "Негатив"),
        (0, "Последние новости"),
        (1, "Позитив"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")

    criterion = models.ForeignKey('evaluation.EvalCriterion', on_delete=models.CASCADE, null=True, blank=True, verbose_name="Критерий")
    topic_modelling_name = models.TextField(verbose_name="Название тематической модели")

    subscription_type = models.SmallIntegerField(choices=TYPES, verbose_name="Тип подписки")
    threshold = models.FloatField(null=True, blank=True, verbose_name="Порог критерия")

    is_active = models.BooleanField(default=True, verbose_name="Активен")
    is_fast = models.BooleanField(default=False, verbose_name="Оперативный")

    def __str__(self):
        return f"Подписка {self.user} на {self.criterion} по {self.topic_modelling_name}"


class SubscriptionReportObject(models.Model):
    class Meta:
        verbose_name = "Объект отчёта по подписке"
        verbose_name_plural = "Объекты отчётов по подпискам"
        unique_together = ('subscription', 'url', 'source', )

    subscription = models.ForeignKey('Subscription', on_delete=models.CASCADE, verbose_name="Подписка")
    url = models.CharField(max_length=1000, null=True, blank=True, unique=True, verbose_name="URL")
    source = models.ForeignKey('Source', on_delete=models.CASCADE, verbose_name="Источник")

    is_sent = models.BooleanField(default=False, verbose_name="Отправлен")

    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания объекта")

    def __str__(self):
        return f"Объект отчёта по {self.subscription} ({self.url})"