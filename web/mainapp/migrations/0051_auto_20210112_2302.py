# Generated by Django 2.2.13 on 2021-01-12 17:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0050_subscription_keyword_query_occurrence_threshold'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscription',
            name='keyword_query_occurrence_threshold',
            field=models.IntegerField(default=1, verbose_name='Минимальное количество вхождений ключевых слов'),
        ),
    ]