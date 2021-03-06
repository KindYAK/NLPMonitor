# Generated by Django 2.2.13 on 2020-09-29 06:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scraping', '0005_auto_20200928_1749'),
    ]

    operations = [
        migrations.AlterField(
            model_name='socialnetworkaccount',
            name='is_valid',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Непроверенный'), (1, 'Верифицированный'), (2, 'Неверифицированный')], default=1, max_length=1000, verbose_name='Состояние аккаунта'),
        ),
        migrations.AlterField(
            model_name='socialnetworkaccount',
            name='nickname',
            field=models.CharField(blank=True, max_length=1000, null=True, verbose_name='Никнэйм аккаунта'),
        ),
    ]
