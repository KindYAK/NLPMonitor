from django.db import models


class Area(models.Model):
    class Meta:
        verbose_name = 'Область'
        verbose_name_plural = 'Область'

    name = models.CharField(max_length=50, blank=False, null=False, unique=True)

    def __str__(self):
        return f'Область - {self.name}'


class District(models.Model):
    class Meta:
        verbose_name = 'Район'
        verbose_name_plural = 'Район'

    name = models.CharField(max_length=50, blank=False, null=False, unique=True)
    area = models.ForeignKey(Area, on_delete=models.CASCADE)

    def __str__(self):
        return f'Район - {self.name}'


class Locality(models.Model):
    class Meta:
        verbose_name = 'Населенный пункт'
        verbose_name_plural = 'Населенный пункт'
        unique_together = ['name', 'district']

    name = models.CharField(verbose_name='Населенный пункт', max_length=50, null=False, blank=False)
    kato_code = models.BigIntegerField(verbose_name='Код КАТО', blank=False, null=False, unique=True)
    latitude = models.CharField(verbose_name='Широта', blank=True, null=True, max_length=50)
    longitude = models.CharField(verbose_name='Долгота', blank=True, null=True, max_length=50)
    district = models.ForeignKey(District, on_delete=models.CASCADE)

    def __str__(self):
        return f'Населенный пункт - {self.name}'
