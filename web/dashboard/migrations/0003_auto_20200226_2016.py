# Generated by Django 2.2.10 on 2020-02-26 14:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0002_auto_20200226_1551'),
    ]

    operations = [
        migrations.AlterField(
            model_name='widget',
            name='index',
            field=models.SmallIntegerField(default=5, verbose_name='Порядковый номер'),
        ),
    ]
