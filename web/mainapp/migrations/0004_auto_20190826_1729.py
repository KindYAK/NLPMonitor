# Generated by Django 2.2.4 on 2019-08-26 11:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0003_auto_20190627_1720'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='unique_hash',
            field=models.CharField(blank=True, max_length=32, null=True, unique=True, verbose_name='Уникальность source, datetime, title'),
        ),
    ]