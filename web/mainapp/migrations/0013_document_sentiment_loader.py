# Generated by Django 2.2.4 on 2019-12-04 04:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0012_auto_20191203_1022'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='sentiment_loader',
            field=models.SmallIntegerField(blank=True, null=True, verbose_name='Тональность'),
        ),
    ]
