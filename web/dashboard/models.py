from django.db import models
from picklefield import PickledObjectField


class DashboardPreset(models.Model):
    class Meta:
        verbose_name = "Пресет дашборда"
        verbose_name_plural = "Пресеты дашбордов"

    name = models.CharField(max_length=50, unique=True, verbose_name="Название")
    corpus = models.ForeignKey('mainapp.Corpus', on_delete=models.CASCADE, verbose_name="Корпус")
    topic_modelling_name = models.CharField(max_length=100, verbose_name="Название ТМ")
    widgets = models.ManyToManyField('Widget', blank=True)

    def __str__(self):
        return f"Dashboard - {self.name}"


class Widget(models.Model):
    class Meta:
        verbose_name = "Виджет"
        verbose_name_plural = "Виджеты"

    TYPES = (
        (0, 'Overall positive-negative'),
        (1, 'Dynamic'),
        (2, 'Top news'),
        (3, 'Top topics'),
        (4, 'Source distribution'),
    )

    TYPES_DICT = dict(TYPES)

    type = models.SmallIntegerField(choices=TYPES, default=0)
    title = models.CharField(max_length=50, verbose_name="Заголовок")
    icon_class = models.CharField(max_length=50, verbose_name="Class иконки")
    index = models.SmallIntegerField(default=0, verbose_name="Порядковый номер")
    criterion = models.ForeignKey("evaluation.EvalCriterion", on_delete=models.CASCADE)
    params = PickledObjectField(null=True, blank=True)

    def __str__(self):
        return f"Виджет -{self.title}"
