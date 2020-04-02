# Generated by Django 2.2.8 on 2020-03-27 10:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0004_auto_20200327_1219'),
    ]

    operations = [
        migrations.AddField(
            model_name='widget',
            name='datetime_from',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Отфильтровать с'),
        ),
        migrations.AddField(
            model_name='widget',
            name='datetime_to',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Отфильтровать до'),
        ),
        migrations.AddField(
            model_name='widget',
            name='days_before_now',
            field=models.IntegerField(blank=True, null=True, verbose_name='Дней назад'),
        ),
        migrations.AlterField(
            model_name='widget',
            name='type',
            field=models.SmallIntegerField(choices=[(0, 'Overall positive-negative'), (1, 'Dynamic'), (2, 'Top news'), (5, 'Bottom news'), (6, 'Last news'), (3, 'Top topics'), (4, 'Source distribution')], default=0),
        ),
    ]