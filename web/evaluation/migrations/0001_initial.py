# Generated by Django 2.2.2 on 2019-06-27 04:14

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DocumentEval',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.FloatField()),
            ],
            options={
                'verbose_name': 'Оценка документа',
                'verbose_name_plural': 'Оценки документов',
            },
        ),
        migrations.CreateModel(
            name='EvalCorpus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=25)),
            ],
            options={
                'verbose_name': 'Корпус оценок',
                'verbose_name_plural': 'Корпусы оценок',
            },
        ),
        migrations.CreateModel(
            name='EvalCriterion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
            ],
            options={
                'verbose_name': 'Критерий оценки',
                'verbose_name_plural': 'Критерии оценки',
            },
        ),
    ]
