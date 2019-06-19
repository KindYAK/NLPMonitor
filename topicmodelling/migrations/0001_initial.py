# Generated by Django 2.2.2 on 2019-06-19 11:43

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
                ('name', models.CharField(blank=True, max_length=250, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='TopicUnit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('weight', models.FloatField(blank=True, null=True)),
                ('text', models.CharField(max_length=100)),
                ('topic', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='topicmodelling.Topic')),
            ],
        ),
        migrations.CreateModel(
            name='TopicCorpus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('description', models.TextField()),
                ('corpus', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mainapp.Corpus')),
            ],
        ),
        migrations.AddField(
            model_name='topic',
            name='topic_corpus',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='topicmodelling.TopicCorpus'),
        ),
        migrations.AddField(
            model_name='topic',
            name='topic_parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='topicmodelling.Topic'),
        ),
        migrations.CreateModel(
            name='DocumentTopic',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('weight', models.FloatField(blank=True, null=True)),
                ('document', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mainapp.Document')),
                ('topic', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='topicmodelling.Topic')),
            ],
        ),
    ]
