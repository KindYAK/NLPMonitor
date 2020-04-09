from django.db import models


class Area(models.Model):
    class Meta:
        verbose_name = 'Область'
        verbose_name_plural = 'Область'

    area_name = models.CharField(max_length=50, blank=False, null=False, unique=True)

    def __str__(self):
        return f'Область - {self.area_name}'


class District(models.Model):
    class Meta:
        verbose_name = 'Район'
        verbose_name_plural = 'Район'

    district_name = models.CharField(max_length=50, blank=False, null=False, unique=True)
    area = models.ForeignKey(Area, on_delete=models.CASCADE)

    def __str__(self):
        return f'Район - {self.district_name}'


class Locality(models.Model):
    class Meta:
        verbose_name = 'Населенный пункт'
        verbose_name_plural = 'Населенный пункт'
        unique_together = ['locality_name', 'district']

    locality_name = models.CharField(verbose_name='Населенный пункт', max_length=50, null=False, blank=False)
    kato_code = models.BigIntegerField(verbose_name='Код КАТО', blank=False, null=False, unique=True)
    latitude = models.FloatField(verbose_name='Широта', blank=True, null=True)
    longitude = models.FloatField(verbose_name='Долгота', blank=True, null=True)
    district = models.ForeignKey(District, on_delete=models.CASCADE)

    def __str__(self):
        return f'Населенный пункт - {self.locality_name}'
