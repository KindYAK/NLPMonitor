# Generated by Django 2.2.13 on 2020-09-26 12:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scraping', '0002_auto_20200926_1848'),
    ]

    operations = [
        migrations.AddField(
            model_name='socialnetworkaccount',
            name='name',
            field=models.CharField(default='', max_length=100, verbose_name='Название'),
            preserve_default=False,
        ),
    ]
