# Generated by Django 2.2.10 on 2020-02-26 06:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('evaluation', '0008_auto_20200105_1727'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='evalcorpus',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='evalcorpus',
            name='corpus',
        ),
        migrations.DeleteModel(
            name='DocumentEval',
        ),
        migrations.DeleteModel(
            name='EvalCorpus',
        ),
    ]
