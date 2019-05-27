# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from .models import YearSettings, Grado, Seccion, Subject, Teacher, ApoderadoUser, Student, Matricula, Tutor, Grade
from .logic import computeAverageGrade, computeMonthlyAverageGrade, computeBiMonthlyAverageGrade

# Create your tests here.

class StudentTest(TestCase):
  def setUp(self):
    year = YearSettings.objects.create(year=2019, 
            start_date="2019-03-04",
            end_date="2019-12-14",
            holidays=[
              "2019-04-18", 
              "2019-04-19", 
              "2019-04-20", 
              "2019-05-01", 
              "2019-06-29", 
              "2019-08-30", 
              "2019-10-08", 
              "2019-10-31", 
              "2019-12-08"],
            periods=[
              { "start": "2019-03-04", "end": "2019-04-06" }, 
              { "start": "2019-04-08", "end": "2019-05-11" }, 
              { "start": "2019-05-13", "end": "2019-06-15" }, 
              { "start": "2019-06-17", "end": "2019-07-20" }, 
              { "start": "2019-08-05", "end": "2019-09-07" }, 
              { "start": "2019-09-09", "end": "2019-10-12" }, 
              { "start": "2019-10-14", "end": "2019-11-16" }, 
              { "start": "2019-11-18", "end": "2019-12-14" }]
            )
    # Usual grados
    cuarto = Grado.objects.create(name="Cuarto de secundaria", 
            grado=4,
            is_saturday_allowed=False)
    # Quinto
    quinto = Grado.objects.create(name="Quinto de secundaria",
            grado=5,
            is_saturday_allowed=True)
    # Seleccion
    selecc = Grado.objects.create(name="Seleccion",
            grado=6,
            is_saturday_allowed=False)
    # Academia
    academ = Grado.objects.create(name="Academia",
            grado=7,
            is_saturday_allowed=True)
    # Una seccion por grado para probar
    cto_a = Seccion.objects.create(section='A', name="", grado=cuarto)
    qto_a = Seccion.objects.create(section='A', name="", grado=quinto)
    sel_a = Seccion.objects.create(section='A', name="", grado=selecc)
    aca_a = Seccion.objects.create(section='A', name="", grado=academ)

    # Cursos por seccion
    curso1 = Subject.objects.create(name="Matematica",
            schedule=[
                  {
                      "day":"Lunes",
                      "start": "8:00",
                      "duration": 2
                  },
                  {
                      "day":"Miercoles",
                      "start": "10:15",
                      "duration": 1
                  }
                ],
            seccion = cto_a)
    curso2 = Subject.objects.create(name="Lenguaje",
            schedule=[
                  {
                      "day":"Lunes",
                      "start": "8:00",
                      "duration": 2
                  },
                  {
                      "day":"Miercoles",
                      "start": "10:15",
                      "duration": 1
                  }
                ],
            seccion = qto_a)
    curso3 = Subject.objects.create(name="Fisica",
            schedule=[
                  {
                      "day":"Lunes",
                      "start": "8:00",
                      "duration": 2
                  },
                  {
                      "day":"Miercoles",
                      "start": "10:15",
                      "duration": 1
                  }
                ],
            seccion = sel_a)
    curso4 = Subject.objects.create(name="Quimica",
            schedule=[
                  {
                      "day":"Lunes",
                      "start": "8:00",
                      "duration": 2
                  },
                  {
                      "day":"Miercoles",
                      "start": "10:15",
                      "duration": 1
                  }
                ],
            seccion = aca_a)

    # Cuentas de profes
    profe1 = Teacher.objects.create(dni=11112222,
            first_name = "Profesor",
            last_name = "de Prueba 1",
            username = "profe1")
    profe2 = Teacher.objects.create(dni=33334444,
            first_name = "Profesor",
            last_name = "de Prueba 2",
            username = "profe2")
    profe3 = Teacher.objects.create(dni=55556666,
            first_name = "Profesor",
            last_name = "de Prueba 3",
            username = "profe3")
    profe4 = Teacher.objects.create(dni=77778888,
            first_name = "Profesor",
            last_name = "de Prueba 4",
            username = "profe4")

    # Cuentas de apoderados
    apod1 = ApoderadoUser.objects.create(dni=11111101,
            first_name = "Apoderado",
            last_name = "1",
            username = "apod1")
    apod2 = ApoderadoUser.objects.create(dni=11111102,
            first_name = "Apoderado",
            last_name = "2",
            username = "apod2")
    apod3 = ApoderadoUser.objects.create(dni=11111103,
            first_name = "Apoderado",
            last_name = "3",
            username = "apod3")
    apod4 = ApoderadoUser.objects.create(dni=11111104,
            first_name = "Apoderado",
            last_name = "4",
            username = "apod4")

    # Estudiantes
    stude1 = Student.objects.create(dni=22222201,
            first_name = "Estudiante",
            last_name = "1",
            apoderado = apod1)
    stude2 = Student.objects.create(dni=22222202,
            first_name = "Estudiante",
            last_name = "2",
            apoderado = apod2)
    stude3 = Student.objects.create(dni=22222203,
            first_name = "Estudiante",
            last_name = "3",
            apoderado = apod3)
    stude4 = Student.objects.create(dni=22222204,
            first_name = "Estudiante",
            last_name = "4",
            apoderado = apod4)

    # Matriculas
    Matricula.objects.create(yearsettings = year,
            student = stude1,
            seccion = cto_a)
    Matricula.objects.create(yearsettings = year,
            student = stude2,
            seccion = qto_a)
    Matricula.objects.create(yearsettings = year,
            student = stude3,
            seccion = sel_a)
    Matricula.objects.create(yearsettings = year,
            student = stude4,
            seccion = aca_a)

    # Tutores
    tutor1 = Tutor.objects.create(teacher = profe1,
            seccion = cto_a,
            year = year)
    tutor2 = Tutor.objects.create(teacher = profe2,
            seccion = qto_a,
            year = year)
    tutor3 = Tutor.objects.create(teacher = profe3,
            seccion = sel_a,
            year = year)
    tutor4 = Tutor.objects.create(teacher = profe4,
            seccion = aca_a,
            year = year)

    # Notas
#      May 2019      
#Su Mo Tu We Th Fr Sa
#          1  2  3  4 
# 5  6  7  8  9 10 11 
#12 13 14 15 16 17 18 
#19 20 21 22 23 24 25 
#26 27 28 29 30 31    
    # Tareas diarias, para estudiante de 4to a
    Grade.objects.create(subject = curso1, student = stude1,
            grade = 18, date = "2019-05-06", grade_type = 1)
    Grade.objects.create(subject = curso1, student = stude1,
            grade = 15, date = "2019-05-07", grade_type = 1)
    Grade.objects.create(subject = curso1, student = stude1,
            grade = 13, date = "2019-05-09", grade_type = 1)
    Grade.objects.create(subject = curso1, student = stude1,
            grade = 19, date = "2019-05-10", grade_type = 1)
    # Evaluaciones diarias, para estudiante de 4to a
    Grade.objects.create(subject = curso1, student = stude1,
            grade = 20, date = "2019-05-06", grade_type = 2)
    Grade.objects.create(subject = curso1, student = stude1,
            grade = 15, date = "2019-05-07", grade_type = 2)
    Grade.objects.create(subject = curso1, student = stude1,
            grade = 11, date = "2019-05-08", grade_type = 2)
    Grade.objects.create(subject = curso1, student = stude1,
            grade = 15, date = "2019-05-10", grade_type = 2)
    # Examen mensual
    Grade.objects.create(subject = curso1, student = stude1,
            grade = 12, period = 1, grade_type = 4)
    # Cuaderno
    Grade.objects.create(subject = curso1, student = stude1,
            grade = 15, period = 1, grade_type = 5)

#     April 2019             May 2019              June 2019     
#Su Mo Tu We Th Fr Sa  Su Mo Tu We Th Fr Sa  Su Mo Tu We Th Fr Sa
#    1  2  3  4  5  6            1  2  3  4                     1 
# 7  8  9 10 11 12 13   5  6  7  8  9 10 11   2  3  4  5  6  7  8 
#14 15 16 17 18 19 20  12 13 14 15 16 17 18   9 10 11 12 13 14 15 
#21 22 23 24 25 26 27  19 20 21 22 23 24 25  16 17 18 19 20 21 22 
#28 29 30              26 27 28 29 30 31     23 24 25 26 27 28 29 
#                                            30                   

    # Tareas diarias, para estudiante de 4to a
    Grade.objects.create(subject = curso1, student = stude1,
            grade = 17, date = "2019-06-03", grade_type = 1)
    Grade.objects.create(subject = curso1, student = stude1,
            grade = 16, date = "2019-06-04", grade_type = 1)
    Grade.objects.create(subject = curso1, student = stude1,
            grade = 11, date = "2019-06-05", grade_type = 1)
    Grade.objects.create(subject = curso1, student = stude1,
            grade = 10, date = "2019-06-06", grade_type = 1)
    # Evaluaciones diarias, para estudiante de 4to a
    Grade.objects.create(subject = curso1, student = stude1,
            grade = 18, date = "2019-05-18", grade_type = 2)
    Grade.objects.create(subject = curso1, student = stude1,
            grade = 19, date = "2019-05-19", grade_type = 2)
    Grade.objects.create(subject = curso1, student = stude1,
            grade = 16, date = "2019-05-20", grade_type = 2)
    Grade.objects.create(subject = curso1, student = stude1,
            grade = 18, date = "2019-05-21", grade_type = 2)
    # Examen mensual
    Grade.objects.create(subject = curso1, student = stude1,
            grade = 18, period = 3, grade_type = 4)
    # Cuaderno
    Grade.objects.create(subject = curso1, student = stude1,
            grade = 12, period = 3, grade_type = 5)
                     
  def test_all(self):
    ys = YearSettings.objects.get(year=2019)
    self.assertEqual(ys.year, 2019)

    #self.test_computeAverageGrade()
    #self.test_computeMonthlyAverageGrade()
    #self.test_computeBiMonthlyAverageGrade()

  def test_computeAverageGrade(self):
    student = Student.objects.get(dni=22222201)
    curso = Subject.objects.get(name="Matematica")
    expected_avg = 14
    period = { "start": "2019-06-01", "end": "2019-06-30" }
    avg = computeAverageGrade(student, curso, 1, period)
    self.assertEqual(avg, expected_avg)

  def test_computeMonthlyAverageGrade(self):
    student = Student.objects.get(dni=22222201)
    curso = Subject.objects.get(name="Matematica")
    ys = YearSettings.objects.get(year=2019)
    expected_avg = {
      "subject_name" : "Matematica",
      "period" : 3,
      "pe": 18, #weight: 2
      "pt": 14, #weight: 2
      "nc": 12, #weight: 1
      "em": 18, #weight: 5
      "pm": 17
    }
    period = 3
    grading_info = {
      "has_dailyeval_grade": True,
      "has_homeworks":       True,
      "has_notebook_grade":  True,
      "has_monthly_exam":    True,
    }
    avg = computeMonthlyAverageGrade(student, curso, ys.periods, period, grading_info)
    print(avg)
    self.assertEqual(avg, expected_avg)
    
  def test_computeBiMonthlyAverageGrade(self):
    p1 = { "pm": "17" }
    p2 = { "pm": "16" }
    avg = computeBiMonthlyAverageGrade(p1, p2)
    expected_avg = 17
    self.assertEqual(avg, expected_avg)
