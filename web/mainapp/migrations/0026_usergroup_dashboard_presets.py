# Generated by Django 2.2.10 on 2020-02-26 09:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0001_initial'),
        ('mainapp', '0025_remove_document_topics'),
    ]

    operations = [
        migrations.AddField(
            model_name='usergroup',
            name='dashboard_presets',
            field=models.ManyToManyField(blank=True, to='dashboard.DashboardPreset'),
        ),
    ]