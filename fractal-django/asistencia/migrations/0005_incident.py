# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2019-09-21 17:15
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('asistencia', '0004_auto_20190921_0854'),
    ]

    operations = [
        migrations.CreateModel(
            name='Incident',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('points', models.IntegerField(blank=True, null=True)),
                ('date', models.DateField(blank=True, default=django.utils.timezone.now, null=True, verbose_name='Fecha')),
                ('incident', models.TextField()),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='asistencia.Student')),
            ],
            options={
                'verbose_name': 'Incidente',
                'verbose_name_plural': 'Incidentes',
            },
        ),
    ]
