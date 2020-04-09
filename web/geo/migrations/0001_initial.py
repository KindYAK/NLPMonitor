# Generated by Django 2.2.10 on 2020-04-07 14:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Area',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('area_name', models.CharField(max_length=50, unique=True)),
            ],
            options={
                'verbose_name': 'Область',
                'verbose_name_plural': 'Область',
            },
        ),
        migrations.CreateModel(
            name='District',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('district_name', models.CharField(max_length=50, unique=True)),
                ('area', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='geo.Area')),
            ],
            options={
                'verbose_name': 'Район',
                'verbose_name_plural': 'Район',
            },
        ),
        migrations.CreateModel(
            name='Locality',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('locality_name', models.CharField(max_length=50, verbose_name='Населенный пункт')),
                ('kato_code', models.BigIntegerField(unique=True, verbose_name='Код КАТО')),
                ('latitude', models.FloatField(blank=True, null=True, verbose_name='Широта')),
                ('longitude', models.FloatField(blank=True, null=True, verbose_name='Долгота')),
                ('district', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='geo.District')),
            ],
            options={
                'verbose_name': 'Населенный пункт',
                'verbose_name_plural': 'Населенный пункт',
                'unique_together': {('locality_name', 'district')},
            },
        ),
    ]