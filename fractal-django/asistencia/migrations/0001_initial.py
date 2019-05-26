# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2019-05-04 19:52
from __future__ import unicode_literals

import datetime
from django.conf import settings
import django.contrib.auth.models
import django.contrib.postgres.fields
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0008_alter_user_username_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='ApoderadoUser',
            fields=[
                ('user_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('dni', models.IntegerField()),
            ],
            options={
                'verbose_name': 'Apoderado',
                'verbose_name_plural': 'Apoderados',
            },
            bases=('auth.user',),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Asistencia',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hour', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Hora de entrada')),
            ],
        ),
        migrations.CreateModel(
            name='Grade',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('grade', models.IntegerField()),
                ('date', models.DateField(blank=True, default=django.utils.timezone.now, null=True, verbose_name='Fecha')),
                ('period', models.IntegerField(blank=True, null=True)),
                ('grade_type', models.IntegerField(choices=[(1, 'tarea'), (2, 'evaluacion'), (3, 'conducta'), (4, 'examen'), (5, 'cuaderno')], default=1, verbose_name='Tipo de nota')),
            ],
            options={
                'verbose_name': 'Nota',
                'verbose_name_plural': 'Notas',
            },
        ),
        migrations.CreateModel(
            name='Grado',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('grado', models.IntegerField()),
                ('entrada', models.TimeField(default=datetime.time(7, 45))),
                ('is_saturday_allowed', models.BooleanField(default=False, verbose_name='Tiene clase los sabados?')),
                ('has_monthly_exam', models.BooleanField(default=True, verbose_name='Tiene examen mensual?')),
                ('has_notebook_grade', models.BooleanField(default=True, verbose_name='Tiene nota de cuaderno mensual?')),
                ('has_homeworks', models.BooleanField(default=True, verbose_name='Tiene tareas diarias?')),
                ('has_dailyeval_grade', models.BooleanField(default=True, verbose_name='Tiene evaluaciones diarias?')),
                ('has_bimonthly_grade', models.BooleanField(default=True, verbose_name='Tiene promedio bimestral?')),
                ('has_simulacros', models.BooleanField(default=False, verbose_name='Tiene simulacros semanales?')),
            ],
        ),
        migrations.CreateModel(
            name='Matricula',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('section', models.CharField(choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')], default='A', max_length=2, verbose_name='Seccion')),
                ('schedule', models.TextField()),
                ('grade', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='asistencia.Grado')),
            ],
            options={
                'verbose_name': 'Horario',
                'verbose_name_plural': 'Horarios',
            },
        ),
        migrations.CreateModel(
            name='Seccion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('section', models.CharField(choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')], default='A', max_length=2, verbose_name='Seccion')),
                ('name', models.CharField(blank=True, max_length=30)),
                ('grado', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='asistencia.Grado')),
            ],
            options={
                'verbose_name': 'Seccion',
                'verbose_name_plural': 'Secciones',
            },
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('f_first_name', models.CharField(max_length=200, verbose_name='Nombre del Padre')),
                ('f_last_name', models.CharField(max_length=200, verbose_name='Apellido del Padre')),
                ('m_first_name', models.CharField(max_length=200, verbose_name='Nombre de la Madre')),
                ('m_last_name', models.CharField(max_length=200, verbose_name='Apellido de la Madre')),
                ('first_name', models.CharField(max_length=200, verbose_name='Nombre del Estudiante')),
                ('last_name', models.CharField(max_length=200, verbose_name='Apellido del Estudiante')),
                ('dni', models.IntegerField(verbose_name='DNI')),
                ('apoderado', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='asistencia.ApoderadoUser')),
            ],
            options={
                'verbose_name': 'Estudiante',
                'verbose_name_plural': 'Estudiantes',
            },
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Curso')),
                ('schedule', django.contrib.postgres.fields.jsonb.JSONField(verbose_name='Horario')),
                ('seccion', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='asistencia.Seccion')),
            ],
            options={
                'verbose_name': 'Curso',
                'verbose_name_plural': 'Cursos',
            },
        ),
        migrations.CreateModel(
            name='Teacher',
            fields=[
                ('user_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('dni', models.IntegerField()),
            ],
            options={
                'verbose_name': 'Profesor',
                'verbose_name_plural': 'Profesores',
            },
            bases=('auth.user',),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Tutor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('seccion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='asistencia.Seccion')),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='asistencia.Teacher')),
            ],
            options={
                'verbose_name': 'Tutor',
                'verbose_name_plural': 'Tutores',
            },
        ),
        migrations.CreateModel(
            name='YearSettings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.IntegerField(verbose_name='Year')),
                ('start_date', models.DateField(default=django.utils.timezone.now, verbose_name='Inicio del ano escolar')),
                ('end_date', models.DateField(default=django.utils.timezone.now, verbose_name='Fin del ano escolar')),
                ('holidays', django.contrib.postgres.fields.ArrayField(base_field=models.DateField(blank=True, null=True, verbose_name='Feriados'), blank=True, null=True, size=None)),
                ('periods', django.contrib.postgres.fields.jsonb.JSONField(verbose_name='Periodos')),
            ],
            options={
                'verbose_name': 'Configuracion anual',
                'verbose_name_plural': 'Configuraciones anuales',
            },
        ),
        migrations.AddField(
            model_name='tutor',
            name='year',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='asistencia.YearSettings'),
        ),
        migrations.AddField(
            model_name='matricula',
            name='seccion',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='asistencia.Seccion'),
        ),
        migrations.AddField(
            model_name='matricula',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='asistencia.Student'),
        ),
        migrations.AddField(
            model_name='matricula',
            name='yearsettings',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='asistencia.YearSettings'),
        ),
        migrations.AddField(
            model_name='grade',
            name='student',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='asistencia.Student'),
        ),
        migrations.AddField(
            model_name='grade',
            name='subject',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='asistencia.Subject'),
        ),
        migrations.AddField(
            model_name='asistencia',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='asistencia.Student'),
        ),
        migrations.AlterUniqueTogether(
            name='asistencia',
            unique_together=set([('student', 'hour')]),
        ),
    ]
