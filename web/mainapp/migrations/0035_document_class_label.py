# Generated by Django 2.2.13 on 2020-07-11 08:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0034_auto_20200528_1624'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='class_label',
            field=models.IntegerField(blank=True, null=True, verbose_name='Класс (разметка)'),
        ),
    ]
