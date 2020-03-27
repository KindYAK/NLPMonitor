from django.db import models
from picklefield import PickledObjectField

from dashboard.widgets_meta import TYPES_META_DICT


class DashboardPreset(models.Model):
    class Meta:
        verbose_name = "Пресет дашборда"
        verbose_name_plural = "Пресеты дашбордов"

    name = models.CharField(max_length=50, unique=True, verbose_name="Название")
    widgets = models.ManyToManyField('Widget', blank=True)

    def __str__(self):
        return f"Dashboard - {self.name}"


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

    # TODO filters list, data filter from to, filters from analyics, datatime_last (now - num_)

    datetime_from = models.DateField(verbose_name='Отфильтровать с', null=True, blank=True)
    datetime_to = models.DateField(verbose_name='Отфильтровать до', null=True, blank=True)
    days_before_now = models.IntegerField(verbose_name='Дней назад', null=True, blank=True)

    params = PickledObjectField(null=True, blank=True)

    @property
    def template_name(self):
        return TYPES_META_DICT[self.type]['template_name']

    @property
    def callable(self):
        return TYPES_META_DICT[self.type]['callable']

    def __str__(self):
        return f"Виджет - {self.title}"
