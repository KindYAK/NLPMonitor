# Generated by Django 2.2.2 on 2019-06-27 11:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0002_auto_20190627_1014'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='unique_hash',
            field=models.CharField(blank=True, max_length=32, null=True, unique=True, verbose_name='Уникальность document, datetime, text'),
        ),
    ]
