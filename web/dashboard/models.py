import json

from django.db import models

from dashboard.widgets_meta import TYPES_META_DICT


class DashboardPreset(models.Model):
    class Meta:
        verbose_name = "Пресет дашборда"
        verbose_name_plural = "Пресеты дашбордов"

    name = models.CharField(max_length=50, unique=True, verbose_name="Название")
    widgets = models.ManyToManyField('Widget', blank=True)

    def __str__(self):
        return f"Dashboard - {self.name}"


class MonitoringObject(models.Model):
    class Meta:
        verbose_name = "Объекты мониторинга"
        verbose_name_plural = "Объекты мониторинга"

    name_query = models.CharField(verbose_name='Предмет запроса', max_length=100, null=True, blank=True)
    ner_query = models.CharField(verbose_name='Список сущностей', max_length=500, null=True, blank=True)

    def __str__(self):
        return f"Предмет запроса - {self.name_query}"


class Widget(models.Model):
    class Meta:
        verbose_name = "Виджет"
        verbose_name_plural = "Виджеты"

    TYPES = (
        (key, value['name']) for key, value in TYPES_META_DICT.items()
    )

    criterion = models.ForeignKey("evaluation.EvalCriterion", on_delete=models.CASCADE)
    topic_modelling_name = models.CharField(max_length=100, verbose_name="Название ТМ")
    type = models.SmallIntegerField(choices=TYPES, default=0)

    title = models.CharField(max_length=50, verbose_name="Заголовок")
    icon_class = models.CharField(max_length=50, verbose_name="Class иконки")
    index = models.SmallIntegerField(default=5, verbose_name="Порядковый номер")

    datetime_from = models.DateField(verbose_name='Отфильтровать с', null=True, blank=True)
    datetime_to = models.DateField(verbose_name='Отфильтровать до', null=True, blank=True)
    days_before_now = models.IntegerField(verbose_name='Дней назад', null=True, blank=True)
    monitoring_object = models.ForeignKey(MonitoringObject, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Объект мониторинга')

    params = models.TextField(null=True, blank=True)

    @property
    def template_name(self):
        return TYPES_META_DICT[self.type]['template_name']

    @property
    def callable(self):
        return TYPES_META_DICT[self.type]['callable']

    @property
    def params_obj(self):
        return json.loads(self.params)

    def __str__(self):
        return f"Виджет - {self.title}"
