# Generated by Django 2.2.2 on 2019-06-20 07:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('preprocessing', '0002_auto_20190620_1312'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='analysisunit',
            index=models.Index(fields=['processed_document'], name='preprocessi_process_cdddd7_idx'),
        ),
        migrations.AddIndex(
            model_name='processedcorpus',
            index=models.Index(fields=['corpus'], name='preprocessi_corpus__e75e7e_idx'),
        ),
        migrations.AddIndex(
            model_name='processeddocument',
            index=models.Index(fields=['processed_corpus'], name='preprocessi_process_fad705_idx'),
        ),
        migrations.AddIndex(
            model_name='processeddocument',
            index=models.Index(fields=['original_document'], name='preprocessi_origina_41bc68_idx'),
        ),
    ]
