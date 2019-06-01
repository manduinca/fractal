# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
#from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField, JSONField

from django.utils import timezone
from datetime import time
# Create your models here.

# https://docs.djangoproject.com/en/1.11/ref/contrib/auth/
class ApoderadoUser(User):
  dni = models.IntegerField()
  class Meta:
    verbose_name = "Apoderado"
    verbose_name_plural = "Apoderados"
  def __unicode__(self):
    return self.first_name + " " + self.last_name
  def __str__(self):
    return self.first_name + " " + self.last_name

class YearSettings(models.Model):
  year = models.IntegerField("Year")
  start_date = models.DateField("Inicio del ano escolar", default=timezone.now)
  end_date = models.DateField("Fin del ano escolar", default=timezone.now)
  holidays = ArrayField(
          models.DateField("Feriados", null=True, blank=True),
          null=True, blank=True
          )
  periods = JSONField("Periodos") 
  # this is going to have a JSON value like: 
  #     [
  #          {
  #            "start": "2019-03-04",
  #            "end"  : "2019-04-06"
  #          },
  #          {
  #            "start": "2019-04-08",
  #            "end"  : "2019-05-11"
  #          },
  #     ]
  #free_days = ArrayField(
          #models.DateField("Vacaciones", null=True, blank=True),
          #null=True, blank=True
          #)
  
  class Meta:
    verbose_name = "Configuracion anual"
    verbose_name_plural = "Configuraciones anuales"
  def __unicode__(self):
    return str(self.year)
  def __str__(self):
    return str(self.year)

class Grado(models.Model):
  name = models.CharField(max_length=200)
  grado = models.IntegerField()
  entrada = models.TimeField(default=time(hour=7,minute=45))
  is_saturday_allowed = models.BooleanField("Tiene clase los sabados?", default=False)
  has_monthly_exam = models.BooleanField("Tiene examen mensual?", default=True)          # 5
  has_notebook_grade = models.BooleanField("Tiene nota de cuaderno mensual?", default=True)      # 1
  has_homeworks = models.BooleanField("Tiene tareas diarias?", default=True)             # 2
  has_dailyeval_grade = models.BooleanField("Tiene evaluaciones diarias?", default=True) # 2
  has_bimonthly_grade = models.BooleanField("Tiene promedio bimestral?", default=True)   # otherwise, don't compute it
  has_simulacros = models.BooleanField("Tiene simulacros semanales?", default=False)     # the simulacros are weekly
  def __unicode__(self):
    return self.name
  def __str__(self):
    return self.name

class Seccion(models.Model):
  SECTION_CHOICES = (
          ('A', "A"),
          ('B', "B"),
          ('C', "C"),
          ('D', "D"),
          )
  section = models.CharField("Seccion", max_length=2, choices=SECTION_CHOICES, default='A')
  name = models.CharField(max_length=30, blank=True)
  grado = models.ForeignKey(Grado, on_delete=models.CASCADE)
  #tutor = models.ForeignKey(Teacher, on_delete=models.CASCADE)
  class Meta:
    verbose_name = "Seccion"
    verbose_name_plural = "Secciones"
  def __unicode__(self):
    return "{}{} {}".format(
        self.grado.grado, 
        self.section,
        self.name if self.name else "")
  def __str__(self):
    return "{}{} {}".format(
        self.grado.grado, 
        self.section,
        self.name if self.name else "")

class Teacher(User):
  dni = models.IntegerField()
  # the other way around is also possible (set a FK for teacher in the Seccion model)
  # but this way allows many teachrs to be assigned to a seccion, so in case one is sick
  # a substitute can take still access the seccion
  #seccion = models.ForeignKey(Seccion, on_delete=models.CASCADE)
  class Meta:
    verbose_name = "Profesor"
    verbose_name_plural = "Profesores"
  def __unicode__(self):
    return "P: " + self.first_name + " " + self.last_name
  def __str__(self):
    return "P: " + self.first_name + " " + self.last_name

class Tutor(models.Model):
  teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
  seccion = models.ForeignKey(Seccion, on_delete=models.CASCADE)
  year = models.ForeignKey(YearSettings, on_delete=models.CASCADE)
  class Meta:
    verbose_name = "Tutor"
    verbose_name_plural = "Tutores"
  def __unicode__(self):
    return self.teacher.last_name + " " + str(self.seccion) + " - " + str(self.year)
  def __str__(self):
    return self.teacher.last_name + " " + str(self.seccion) + " - " + str(self.year)

class Subject(models.Model):
  name = models.CharField("Curso", max_length=200)
  #schedule = models.CharField("Horario", max_length=200) # this is going to have a JSON value like: [Lu:{ start:8, duration:2 }, Ma: {start:14, duration:2} ]
  schedule = JSONField("Horario") # this is going to have a JSON value like: [Lu:{ start:8, duration:2 }, Ma: {start:14, duration:2} ]
  #teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=True)
  seccion = models.ForeignKey(Seccion, on_delete=models.CASCADE, null=True)
  class Meta:
    verbose_name = "Curso"
    verbose_name_plural = "Cursos"
  def __unicode__(self):
    return "{} {}".format(self.name, self.schedule)
  def __str__(self):
    return "{} {}".format(self.name, self.schedule)

class Student(models.Model):
  f_first_name = models.CharField("Nombre del Padre", max_length=200)
  f_last_name = models.CharField("Apellido del Padre", max_length=200)
  m_first_name = models.CharField("Nombre de la Madre", max_length=200)
  m_last_name = models.CharField("Apellido de la Madre", max_length=200)
  apoderado = models.ForeignKey(ApoderadoUser, on_delete=models.CASCADE)
  first_name = models.CharField("Nombre del Estudiante", max_length=200)
  last_name = models.CharField("Apellido del Estudiante", max_length=200)
  dni = models.IntegerField("DNI")
  #grado = models.IntegerField()
  #grado = models.ForeignKey(Grado, on_delete=models.CASCADE)
  #section = models.CharField("Seccion", max_length=20)
  #SECTION_CHOICES = (
  #        ('A', "A"),
  #        ('B', "B"),
  #        ('C', "C"),
  #        ('D', "D"),
  #        )
  #section = models.CharField("Seccion", max_length=2, choices=SECTION_CHOICES, default='A')
  class Meta:
    verbose_name = "Estudiante"
    verbose_name_plural = "Estudiantes"
  def __unicode__(self):
    return self.first_name + " " + self.last_name
  def __str__(self):
    return self.first_name + " " + self.last_name

#class SubjectStudentMapping(models.Model):
class Matricula(models.Model):
  yearsettings = models.ForeignKey(YearSettings, on_delete=models.CASCADE, null=True)
  # this way a student can be registered in more than one seccion (one could be regular school
  # and the other one could be academia)
  student = models.ForeignKey(Student, on_delete=models.CASCADE)
  seccion = models.ForeignKey(Seccion, on_delete=models.CASCADE, null=True)
  def __unicode__(self):
    return "({}): {},{}".format(self.yearsettings.year, self.student.apoderado.username, self.seccion)
  def __str__(self):
    return "({}): {},{}".format(self.yearsettings.year, self.student.apoderado.username, self.seccion)

class Asistencia(models.Model):
  student = models.ForeignKey(Student, on_delete=models.CASCADE)
  hour = models.DateTimeField("Hora de entrada", default=timezone.now)
  class Meta:
    unique_together = ( 'student','hour')
  def __unicode__(self):
    return str(self.student) + " : " + self.hour.strftime("%d-%m-%Y")
  def __str__(self):
    return str(self.student) + " : " + self.hour.strftime("%d-%m-%Y")

# if subject is null, then the grade is related to the student and a certain time_object: date, week or period
class Grade(models.Model):
  subject = models.ForeignKey(Subject, on_delete=models.CASCADE, null=True)
  student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True)
  grade = models.IntegerField()
  date = models.DateField("Fecha", default=timezone.now, null=True, blank=True) #this is only for types 1,2
  week = models.IntegerField(null=True, blank=True) #this is for type 6
  period = models.IntegerField(null=True, blank=True) #this is for types 3,4,5
  GRADE_TYPES = ( 
          (1, "tarea"),
          (2, "evaluacion"),
          (3, "conducta"),      #This is bi monthly, not related to any subject, just to the student
          (4, "examen"),        #This is monthly
          (5, "cuaderno"),      #This is monthly
          (6, "simulacro"),     #This is weekly, not related to any subject, just to the student
          )
  grade_type = models.IntegerField("Tipo de nota", choices=GRADE_TYPES, default=1)
  class Meta:
    verbose_name = "Nota"
    verbose_name_plural = "Notas"
  def __unicode__(self):
    return "{}".format(self.grade)
  def __str__(self):
    return "{}".format(self.grade)

class Schedule(models.Model):
  grade = models.ForeignKey(Grado, on_delete=models.CASCADE)
  SECTION_CHOICES = (
          ('A', "A"),
          ('B', "B"),
          ('C', "C"),
          ('D', "D"),
          )
  section = models.CharField("Seccion", max_length=2, choices=SECTION_CHOICES, default='A')
  schedule = models.TextField()
  class Meta:
    verbose_name = "Horario"
    verbose_name_plural = "Horarios"
  def __unicode__(self):
    return self.schedule
  def __str__(self):
    return self.schedule

