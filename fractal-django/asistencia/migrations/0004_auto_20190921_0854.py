# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2019-09-21 08:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('asistencia', '0003_grade_week'),
    ]

    operations = [
        migrations.AlterField(
            model_name='grade',
            name='grade_type',
            field=models.IntegerField(choices=[(1, 'tarea'), (2, 'evaluacion'), (3, 'conducta'), (4, 'examen'), (5, 'cuaderno'), (6, 'simulacro'), (7, 'concepto')], default=1, verbose_name='Tipo de nota'),
        ),
    ]
