# Generated by Django 2.2.2 on 2019-06-20 07:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0005_auto_20190620_1317'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='document',
            index=models.Index(fields=['source'], name='mainapp_doc_source__b4a2c7_idx'),
        ),
    ]
