# Generated by Django 2.2.4 on 2019-12-04 11:41

from django.db import migrations, models
import django.db.models.deletion
import picklefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0014_auto_20191204_1050'),
    ]

    operations = [
        migrations.AddField(
            model_name='expert',
            name='corpus',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='mainapp.Corpus', verbose_name='Корпус'),
        ),
        migrations.AddField(
            model_name='viewer',
            name='corpus',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='mainapp.Corpus', verbose_name='Корпус'),
        ),
        migrations.AlterField(
            model_name='expert',
            name='criterions',
            field=models.ManyToManyField(blank=True, to='evaluation.EvalCriterion'),
        ),
        migrations.AlterField(
            model_name='expert',
            name='topic_modelling_names',
            field=picklefield.fields.PickledObjectField(blank=True, editable=False, null=True, verbose_name='Название тематических моделирований'),
        ),
        migrations.AlterField(
            model_name='viewer',
            name='criterions',
            field=models.ManyToManyField(blank=True, to='evaluation.EvalCriterion'),
        ),
        migrations.AlterField(
            model_name='viewer',
            name='topic_modelling_names',
            field=picklefield.fields.PickledObjectField(blank=True, editable=False, null=True, verbose_name='Название тематических моделирований'),
        ),
    ]
