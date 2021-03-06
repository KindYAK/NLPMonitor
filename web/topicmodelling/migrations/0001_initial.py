# Generated by Django 2.2.2 on 2019-06-27 04:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('mainapp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=250, null=True, verbose_name='Название')),
            ],
            options={
                'verbose_name': 'Топик',
                'verbose_name_plural': 'Топики',
            },
        ),
        migrations.CreateModel(
            name='TopicUnit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('weight', models.FloatField(blank=True, null=True, verbose_name='Вес')),
                ('text', models.CharField(max_length=100, verbose_name='Текст')),
                ('unique_hash', models.CharField(blank=True, max_length=32, null=True, unique=True, verbose_name='Уникальность topic, text')),
                ('topic', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='topicmodelling.Topic', verbose_name='Топик')),
            ],
            options={
                'verbose_name': 'Единица-описание топика',
                'verbose_name_plural': 'Единицы-описания топика',
            },
        ),
        migrations.CreateModel(
            name='TopicCorpus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Название')),
                ('description', models.TextField(verbose_name='Описание')),
                ('corpus', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mainapp.Corpus', verbose_name='Корпус')),
            ],
            options={
                'verbose_name': 'Корпус топиков',
                'verbose_name_plural': 'Корпусы топиков',
                'unique_together': {('corpus', 'name')},
            },
        ),
        migrations.AddField(
            model_name='topic',
            name='topic_corpus',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='topicmodelling.TopicCorpus', verbose_name='Корпус топиков'),
        ),
        migrations.AddField(
            model_name='topic',
            name='topic_parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='topicmodelling.Topic', verbose_name='Родительский топик'),
        ),
        migrations.CreateModel(
            name='DocumentTopic',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('weight', models.FloatField(blank=True, null=True, verbose_name='Вес')),
                ('document', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mainapp.Document', verbose_name='Документ')),
                ('topic', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='topicmodelling.Topic', verbose_name='Топик')),
            ],
            options={
                'verbose_name': 'Связь документа и топика',
                'verbose_name_plural': 'Связи документов и топиков',
                'unique_together': {('topic', 'document')},
            },
        ),
    ]
