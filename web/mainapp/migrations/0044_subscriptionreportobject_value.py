# Generated by Django 2.2.13 on 2020-11-18 17:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0043_subscriptionreportobject_title'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscriptionreportobject',
            name='value',
            field=models.FloatField(default=0, verbose_name='Значение критерия'),
        ),
    ]