# Generated by Django 2.2.10 on 2020-05-23 14:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0031_auto_20200519_1844'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='datetime_activity_es_updated',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Дата последнего апдейта активности в ES'),
        ),
    ]
