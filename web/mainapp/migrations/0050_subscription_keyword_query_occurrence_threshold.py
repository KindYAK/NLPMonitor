# Generated by Django 2.2.13 on 2021-01-12 16:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0049_auto_20210112_2238'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscription',
            name='keyword_query_occurrence_threshold',
            field=models.TextField(blank=True, null=True, verbose_name='Минимальное количество вхождений ключевых слов'),
        ),
    ]