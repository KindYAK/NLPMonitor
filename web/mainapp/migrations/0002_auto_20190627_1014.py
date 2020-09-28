# Generated by Django 2.2.2 on 2019-06-27 04:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('mainapp', '0001_initial'),
        ('topicmodelling', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='topics',
            field=models.ManyToManyField(blank=True, through='topicmodelling.DocumentTopic', to='topicmodelling.Topic', verbose_name='Топики'),
        ),
        migrations.AddField(
            model_name='comment',
            name='document',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mainapp.Document', verbose_name='Документ'),
        ),
        migrations.AddField(
            model_name='comment',
            name='reply_to',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='mainapp.Comment', verbose_name='Ответ на...'),
        ),
        migrations.AddField(
            model_name='category',
            name='corpus',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mainapp.Corpus', verbose_name='Корпус'),
        ),
        migrations.AddField(
            model_name='author',
            name='corpus',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mainapp.Corpus', verbose_name='Корпус'),
        ),
        migrations.AddIndex(
            model_name='tag',
            index=models.Index(fields=['corpus'], name='mainapp_tag_corpus__919fb7_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='tag',
            unique_together={('corpus', 'name')},
        ),
        migrations.AlterUniqueTogether(
            name='source',
            unique_together={('corpus', 'name')},
        ),
        migrations.AddIndex(
            model_name='category',
            index=models.Index(fields=['corpus'], name='mainapp_cat_corpus__e53ff8_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='category',
            unique_together={('corpus', 'name')},
        ),
        migrations.AlterUniqueTogether(
            name='author',
            unique_together={('corpus', 'name')},
        ),
    ]
