# Generated by Django 2.2.13 on 2020-10-13 09:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scraping', '0017_auto_20201009_1656'),
    ]

    operations = [
        migrations.AddField(
            model_name='monitoringquery',
            name='max_requests_per_session',
            field=models.PositiveSmallIntegerField(default=100, verbose_name='Количество запросов за сессию'),
        ),
    ]