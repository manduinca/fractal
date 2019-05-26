from django.contrib.auth.models import User
from django.db.models import Avg
from .models import Asistencia, ApoderadoUser, Student, Schedule, YearSettings, Tutor, Subject, Matricula, Grade, Teacher
import math
import logging

def processStudentRequest():
  user = User.objects.get(id=request.user.id)
  data = {}
  return data

# teacher_id: id of the teacher
# ys_id: year settings id
def getGradesByStudentForTeacher( teacher_id, ys_id ):
  logger = logging.getLogger(__name__)
  user = User.objects.get(id=teacher_id)
  data = {}
  data["name"] = user.first_name + " " + user.last_name
  tutor = Tutor.objects.get(teacher_id=user.id, year_id=ys_id )
  data["grado"] = tutor.seccion.grado.name
  data["seccion"] = tutor.seccion.section
  cursos = []
  for s in Subject.objects.filter(seccion_id=tutor.seccion.id).order_by('id'):
    cursos.append({ "name": s.name, "id": s.id })
  students = []
  for m in Matricula.objects.filter(seccion_id=tutor.seccion.id, yearsettings_id=ys_id):
    student = Student.objects.get(id=m.student_id)
    logger.error(student)
    for sub in Subject.objects.filter(seccion_id=m.seccion_id).order_by('id'):
      t = Grade.objects.filter(student_id=student.id, subject_id=sub.id, grade_type=1).first()
      e = Grade.objects.filter(student_id=student.id, subject_id=sub.id, grade_type=2).first()
      students.append(
              { 
                "id": student.id,
                "name": student.first_name + " " + student.last_name, 
                "tarea": "-" if not t else t.grade, 
                "evaluacion": "-" if not e else e.grade, 
                "date": "-",
                "subject": sub.id,
              })
  data["cursos"] = cursos
  data["students"] = students
  return data

def saveGradesForSubject(subject_id, params, date):
  grades = Grade.objects.filter(subject_id=subject_id)
  for (k,v) in params.items():
    logger = logging.getLogger(__name__)
    logger.error("k: {}, v:{}".format(k,v))
    try:
      v = int(v)
    except:
      continue
    if k[0]=='t':
      student_id = k[1:]
      g = Grade.objects.filter(student_id=student_id, 
              subject_id=subject_id, 
              grade_type=1,
              date=date).first()
      if v>=0:
        if not g:
          g = Grade(student_id=student_id, 
                  subject_id=subject_id, 
                  date=date, 
                  grade_type=1, 
                  grade=v)
        else:
          g.grade = v
        g.save()
      else:
        g.delete()
    elif k[0]=='e':
      student_id = k[1:]
      g = Grade.objects.filter(student_id=student_id, 
              subject_id=subject_id, 
              grade_type=2,
              date=date).first()
      if v>=0:
        if not g:
          g = Grade(student_id=student_id, 
                  subject_id=subject_id, 
                  date=date, 
                  grade_type=2, 
                  grade=v)
        else:
          g.grade = v
        g.save()
      else:
        g.delete()
  #for g in grades:
  #  if g.type == "tarea"
  #    params[t
  return ""

# teacher_id: id of the teacher
# ys_id: year settings id
def getGradesBySubjectForTeacher( teacher_id, ys_id, date ):
  logger = logging.getLogger(__name__)
  user = User.objects.get(id=teacher_id)
  teacher = {}
  teacher["name"] = user.first_name + " " + user.last_name
  tutor = Tutor.objects.get(teacher_id=user.id, year_id=ys_id)
  teacher["grado"] = tutor.seccion.grado.name
  teacher["seccion"] = tutor.seccion.section
  teacher["seccion_has_name"] = tutor.seccion.name
  #cursos = []
  #for s in Subject.objects.filter(seccion_id=tutor.seccion.id).order_by('id'):
  #  cursos.append({ "name": s.name, "id": s.id })
  #students = []
  grades = []
  for sub in Subject.objects.filter(seccion_id=tutor.seccion.id).order_by('id'):
    grade = {}
    grade["subject_name"] = sub.name
    grade["subject_id"] = sub.id
    grade["date"] = date
    grade["student"] = []
    for m in Matricula.objects.filter(seccion_id=tutor.seccion.id, yearsettings_id=ys_id).order_by('student__last_name'):
      student = Student.objects.get(id=m.student_id)
      logger.error(student)
      t = Grade.objects.filter(student_id=student.id, 
              subject_id=sub.id, 
              grade_type=1, 
              date=date).first()
      e = Grade.objects.filter(student_id=student.id, 
              subject_id=sub.id, 
              grade_type=2,
              date=date).first()
      grade["student"].append(
              { 
                "student_id": student.id,
                "name": student.first_name + " " + student.last_name, 
                "tarea": "-" if not t else t.grade, 
                "evaluacion": "-" if not e else e.grade, 
                "date": "-" if not e else e.date,
              })
    grades.append(grade)
  #data["cursos"] = cursos
  #data["students"] = students
  #[
  #        { "subject_name" : "matematica",
  #          "subject_id": "3",
  #          "notas": [
  #              "student_id": 2,
  #              "name": "juanito",
  #              "tarea": "30",
  #              "evaluacion": "-",
  #              "date": "03/04/2019",
  #          ]
  #        },
  #]
  return teacher, grades

# returns teacher info and all the grades of the students under responsability
# of the apoderado
def getGradesForStudent( apoderado_id, ys_id, date, grading_info ):
  logger = logging.getLogger(__name__)
  students_grades = []
  teacher = {}
  logger.error(" apoderado_id: {}".format(apoderado_id))
  logger.error(Student.objects.filter(apoderado__id=apoderado_id))
  for s in Student.objects.filter(apoderado__id=apoderado_id):
    student = {}
    student["student_name"] = "{} {}".format(s.first_name, s.last_name)
    grades = []
    #FIXME: it could be possible that a student is registered in more than one class
    matricula = Matricula.objects.filter(yearsettings_id=ys_id,
            student_id=s.id).first()
    teacher = getTeacherInfo(ys_id, matricula)
    for sub in Subject.objects.filter(seccion_id=matricula.seccion_id):
      grade = {}
      has_grade = False
      grade["subject_name"] = sub.name
      if grading_info["has_homeworks"]:
        grade_obj1 = Grade.objects.filter(student_id=s.id, subject_id=sub.id, date=date, grade_type=1).first()
        grade["nota1"] = "-" if not grade_obj1 else grade_obj1.grade
        if grade_obj1:
          has_grade = True
      if grading_info["has_dailyeval_grade"]:
        grade_obj2 = Grade.objects.filter(student_id=s.id, subject_id=sub.id, date=date, grade_type=2).first()
        grade["nota2"] = "-" if not grade_obj2 else grade_obj2.grade
        if grade_obj2:
          has_grade = True
      grade["date"] = date
      if has_grade:
        grades.append(grade)
    student["grades"] = grades
    students_grades.append(student)
    # TODO: implement template for multiple students
    break
  return teacher, students_grades
  #[ 
  #  {
  #    "student_name": "juanito",
  #    "grades":
  #    [
  #      {
  #          "subject_name": "matematica",
  #          "nota1": "20",
  #          "nota2": "15",
  #          "date": "2019-12-1"
  #      },
  #    ]
  #  },
  #]

# teacher_id: id of the teacher
# ys_id: year settings id
def getMonthlyGradesBySubjectForTeacher( teacher_id, ys_id, period, grading_info ):
  logger = logging.getLogger(__name__)
  user = User.objects.get(id=teacher_id)
  teacher = {}
  tutor = Tutor.objects.get(teacher_id=user.id, year_id=ys_id)
  teacher["grado"] = tutor.seccion.grado.name
  teacher["seccion"] = tutor.seccion.section
  teacher["seccion_has_name"] = tutor.seccion.name
  grades = []
  for sub in Subject.objects.filter(seccion_id=tutor.seccion.id).order_by('id'):
    grade = {}
    grade["subject_name"] = sub.name
    grade["subject_id"] = sub.id
    grade["period"] = period
    grade["student"] = []
    for m in Matricula.objects.filter(seccion_id=tutor.seccion.id, yearsettings_id=ys_id).order_by('student__last_name'):
      student = Student.objects.get(id=m.student_id)
      logger.error(student)
      #b = Grade.objects.filter(student_id=student.id, 
      #        subject_id=sub.id, 
      #        grade_type=3, 
      #        period=period).first()

      e = Grade.objects.filter(student_id=student.id, 
              subject_id=sub.id, 
              grade_type=4, 
              period=period).first()
      c = Grade.objects.filter(student_id=student.id, 
              subject_id=sub.id, 
              grade_type=5,
              period=period).first()
      grade["student"].append(
              { 
                "student_id": student.id,
                "name": student.first_name + " " + student.last_name, 
                "examen": "-" if not e else e.grade, 
                "cuaderno": "-" if not c else c.grade, 
                "period": "-" if not c else c.period,
              })
    grades.append(grade)
  #data["cursos"] = cursos
  #data["students"] = students
  #[
  #        { "subject_name" : "matematica",
  #          "subject_id": "3",
  #          "notas": [
  #              "student_id": 2,
  #              "name": "juanito",
  #              "tarea": "30",
  #              "evaluacion": "-",
  #              "date": "03/04/2019",
  #          ]
  #        },
  #]
  return teacher, grades

def saveMonthlyGradesForSubject(subject_id, params, period):
  grades = Grade.objects.filter(subject_id=subject_id)
  for (k,v) in params.items():
    logger = logging.getLogger(__name__)
    logger.error("k: {}, v:{}".format(k,v))
    try:
      v = int(v)
    except:
      continue
    if k[0]=='e':
      student_id = k[1:]
      g = Grade.objects.filter(student_id=student_id, 
              subject_id=subject_id, 
              grade_type=4,
              period=period).first()
      if v>=0:
        if not g:
          g = Grade(student_id=student_id, 
                  subject_id=subject_id, 
                  period=period, 
                  grade_type=4, 
                  grade=v)
        else:
          g.grade = v
        g.save()
      else:
        g.delete()
    elif k[0]=='c':
      student_id = k[1:]
      g = Grade.objects.filter(student_id=student_id, 
              subject_id=subject_id, 
              grade_type=5,
              period=period).first()
      if v>=0:
        if not g:
          g = Grade(student_id=student_id, 
                  subject_id=subject_id, 
                  period=period, 
                  grade_type=5, 
                  grade=v)
        else:
          g.grade = v
        g.save()
      else:
        g.delete()
  return subject_id

def getMonthlyGradesForStudent( apoderado_id, ys_id, periods, period, grading_info ):
  logger = logging.getLogger(__name__)
  students_grades = []
  teacher = {}
  logger.error(" apoderado_id: {}".format(apoderado_id))
  logger.error(Student.objects.filter(apoderado__id=apoderado_id))
  for s in Student.objects.filter(apoderado__id=apoderado_id):
    student = {}
    student["student_name"] = "{} {}".format(s.first_name, s.last_name)
    grades = []
    #FIXME: it could be possible that a student is registered in more than one class
    matricula = Matricula.objects.filter(yearsettings_id=ys_id,
            student_id=s.id).first()

    teacher = getTeacherInfo(ys_id, matricula)
    for sub in Subject.objects.filter(seccion_id=matricula.seccion_id):
      grade = {}
#computeAverageGrade(student_id, subject_id, grade_type, start_date, end_date):
      logger.error("period info: {}".format(periods[int(period)-1]))
      grade = computeMonthlyAverageGrade(s, sub, periods, period, grading_info)
      grades.append(grade)
    student["grades"] = grades
    students_grades.append(student)
    #TODO: implement template for multiple students
    break
  return teacher, students_grades
  #[ 
  #  {
  #    "student_name": "juanito",
  #    "grades":
  #    [
  #      {
  #          "subject_name": "matematica",
  #          "nota1": "20",
  #          "nota2": "15",
  #          "date": "2019-12-1"
  #      },
  #    ]
  #  },
  #]

def computeAverageGrade(student_id, subject_id, grade_type, period ):
  start_date = period["start"]
  end_date   = period["end"]
  grades = Grade.objects.filter(student_id=student_id,
          subject_id=subject_id,
          grade_type=grade_type,
          date__gte=start_date,
          date__lte=end_date)
  if grades:
    return round(grades.aggregate(Avg('grade'))["grade__avg"])
  else:
    return grades.aggregate(Avg('grade'))["grade__avg"]
      

def getFormatedSchedule( apoderado_id, ys_id, is_saturday_allowed ):
  logger = logging.getLogger(__name__)
  student = Student.objects.filter(apoderado__id=apoderado_id).first()
  matricula = Matricula.objects.filter(yearsettings_id=ys_id,
            student_id=student.id).first()
  is_seleccion = False
  if matricula.seccion.grado.name.lower().find("selec") >= 0:
    is_seleccion = True
  schedule = [ ]
  hours = [
    "08:00 - 08:30", #0
    "08:30 - 09:00", #1
    "09:00 - 09:30", #2
    "09:30 - 10:00", #3 ###
    "10:15 - 10:45", #4
    "10:45 - 11:15", #5
    "11:15 - 11:45", #6
    "11:45 - 12:15", #7 ###
    "12:40 - 01:10", #8
    "01:10 - 01:40", #9
    "01:40 - 02:10", #10
    "02:10 - 02:40", #11 ###
    ]
  if is_seleccion:
    hours.extend([
    "03:55 - 04:25", #12
    "04:25 - 04:55", #13
    "04:55 - 05:25"  #14
    ])
  for i in range(0,len(hours)):
    num_cols = 5 if not is_saturday_allowed else 6
    row = [ hours[i] ]
    for j in range(0,num_cols):
      row.append("-")
    schedule.append(row)
  for s in Subject.objects.filter(seccion_id=matricula.seccion.id):
    #format
    #[ { "day":"Jueves", "start": "10:15", "duration: 1, }, { "day":"Sabado", "start": "13:35", "duration": 1 } ]
    for hour in s.schedule:
      col = dayToCol(hour["day"])
      row = hourToRow(hour["start"])
      #duration = mapDurationToArrayIndex(hour["duration"])
      duration = int(hour["duration"]*2)
      for d in range(0, duration):
        schedule[row+d][col] = s.name
  schedule.insert(4,["10:00 - 10:15", "rowspan", "Recreo"])
  schedule.insert(9,["12:15 - 12:40", "rowspan", "Recreo"])
  if is_seleccion:
    schedule.insert(14,["02:40 - 03:55", "rowspan", "Almuerzo"])
    schedule.insert(18,["05:25 - 05:30", "rowspan", "Entrega de Examenes"])
  else:
    schedule.insert(14,["02:40 - 02:45", "rowspan", "Entrega de Cuadernos"])
  # compressSchedule(schedule) #TODO
  return schedule

def dayToCol( day ):
  map = { "lunes": 1, "martes":2, "miercoles":3, "jueves":4, "viernes":5, "sabado":6 }
  return map[day.lower()]

def hourToRow( hour ):
  try:
    map = { 
          "08:00": 0,
          "8:00" : 0,
          "08:30": 1,
          "8:30" : 1,
          "09:00": 2,
          "9:00" : 2,
          "09:30": 3,
          "9:30" : 3,
          "10:15": 4,
          "10:45": 5,
          "11:15": 6,
          "11:45": 7,
          "12:40": 8,
          "01:10": 9,
          "1:10" : 9,
          "13:10": 9,
          "01:40": 10,
          "1:40" : 10,
          "13:40": 10,
          "02:10": 11,
          "2:10" : 11,
          "14:10": 11, # Following is just for seleccion
          "03:55": 12,
          "3:55" : 12,
          "15:55": 12,
          "04:25": 13,
          "4:25" : 13,
          "16:25": 13,
          "04:55": 14,
          "4:55" : 14,
          "16:55": 14,
        }
    return map[hour]
  except KeyError:
    logger = logging.getLogger(__name__)
    logger.error("no hour found for {}".format(hour) +
            "verify the subject start and duration")
    raise KeyError 
    

#def mapDurationToArrayIndex(duration)
#  cols = {
#    1: 0.5,
#    2: 1,
#    3: 1.5,
#    4: 2,

# TODO: this function should remove repeated rows, so the schedule 
# is smaller (compressed) and looks better
#def compressSchedule(schedule):
def getBiMonthlyGradesByStudentForTeacher( teacher_id, ys_id, student_id, periods, bimonth, grading_info ):
  students = []
  grades_for_student = []
  class_info = {}
  tutor = Tutor.objects.get(teacher_id=teacher_id, year_id=ys_id)
  class_info["grado"] = tutor.seccion.grado.name
  class_info["seccion"] = tutor.seccion.section
  class_info["seccion_has_name"] = tutor.seccion.name
  for m in Matricula.objects.filter(seccion_id=tutor.seccion.id, yearsettings_id=ys_id):
    s = Student.objects.get(id=m.student_id)
    student = {}
    student["student_name"] = "{} {}".format(s.first_name, s.last_name)
    student["student_id"] = s.id
    student["is_selected"] = False
    students.append(student)
    if student_id < 0:
      student_id = s.id
    if student_id == s.id:
      student["is_selected"] = True
      for sub in Subject.objects.filter(seccion_id=m.seccion_id).order_by('id'):
        grade = {}
        grade["subject_name"] = sub.name
        pm1 = computeMonthlyAverageGrade(s, sub, periods, bimonth*2-1, grading_info)
        pm2 = computeMonthlyAverageGrade(s, sub, periods, bimonth*2, grading_info)
        pb = computeBiMonthlyAverageGrade( pm1, pm2 )
        grade["pm1"] = pm1["pm"]
        grade["pm2"] = pm2["pm"]
        grade["pb"] = "-" if not pb else pb
        grade["bimonth"] = bimonth
        grades_for_student.append(grade)
      
  return class_info, students, grades_for_student

def getBiMonthlyGradesForStudent( apoderado_id, ys_id, periods, bimonth, grading_info ):
  logger = logging.getLogger(__name__)
  students_grades = []
  teacher = {}
  logger.error(" apoderado_id: {}".format(apoderado_id))
  logger.error(Student.objects.filter(apoderado__id=apoderado_id))
  for s in Student.objects.filter(apoderado__id=apoderado_id):
    student = {}
    student["student_name"] = "{} {}".format(s.first_name, s.last_name)
    grades = []
    #FIXME: it could be possible that a student is registered in more than one class
    matricula = Matricula.objects.filter(yearsettings_id=ys_id,
            student_id=s.id).first()

    teacher = getTeacherInfo(ys_id, matricula)
    for sub in Subject.objects.filter(seccion_id=matricula.seccion_id):
      grade = {}
      grade["subject_name"] = sub.name
      pm1 = computeMonthlyAverageGrade(s, sub, periods, bimonth*2-1, grading_info)
      pm2 = computeMonthlyAverageGrade(s, sub, periods, bimonth*2, grading_info)
      pb = computeBiMonthlyAverageGrade( pm1, pm2 )
      grade["pm1"] = pm1["pm"]
      grade["pm2"] = pm2["pm"]
      grade["pb"] = "-" if not pb else pb
      grade["bimonth"] = bimonth
      grades.append(grade)
    student["grades"] = grades
    students_grades.append(student)
    #TODO: implement template for multiple students
    break
  return teacher, students_grades

# this computes the month average for a given student and subject, in the required period according to the periods and grading_info
def computeMonthlyAverageGrade(student, subject, periods, period, grading_info):
  has_monthly_avg = True
  weights = 0
  grade = {}
  grade["pm"] = 0
  if grading_info["has_dailyeval_grade"]:
    weight = 2
    evaluacion_avg  = computeAverageGrade(student.id, subject.id, 2, periods[int(period)-1])
    if not evaluacion_avg:
      grade["pe"] = "-"
      has_monthly_avg = False
    else:
      grade["pe"] = evaluacion_avg
      grade["pm"] += evaluacion_avg*weight
    weights += weight

  if grading_info["has_homeworks"]:
    weight = 2
    tareas_avg = computeAverageGrade(student.id, subject.id, 1, periods[int(period)-1])
    if not tareas_avg:
      grade["pt"] = "-"
      has_monthly_avg = False
    else:
      grade["pt"] = tareas_avg
      grade["pm"] += tareas_avg*weight
    weights += weight

  if grading_info["has_notebook_grade"]:
    weight = 1
    grade_cuaderno = Grade.objects.filter(student_id=student.id, subject_id=subject.id, period=period, grade_type=5).first()
    if not grade_cuaderno:
      grade["nc"] = "-"
      has_monthly_avg = False
    else:
      grade["nc"] = grade_cuaderno.grade
      grade["pm"] += grade_cuaderno.grade*weight
    weights += weight

  if grading_info["has_monthly_exam"]:
    weight = 5
    grade_examen = Grade.objects.filter(student_id=student.id, subject_id=subject.id, period=period, grade_type=4).first()
    if not grade_examen:
      grade["em"] = "-"
      has_monthly_avg = False
    else:
      grade["em"] = grade_examen.grade
      grade["pm"] += grade_examen.grade*weight
    weights += weight

  grade["subject_name"] = subject.name
  grade["period"] = period
  grade["pm"] = "-" if not has_monthly_avg else round((grade["pm"])/weights)
  return grade

def computeBiMonthlyAverageGrade( pm1, pm2 ):
  p1 = pm1["pm"]
  p2 = pm2["pm"]
  if p1=="-" or p2=="-":
    return None
  else:
    return round((int(p1) + int(p2))/2)

def getTeacherInfo(ys_id, matricula):
  teacher = {}
  tutor_obj = Tutor.objects.filter(year_id=ys_id, seccion_id=matricula.seccion.id).first()
  teacher_obj = Teacher.objects.get(id=tutor_obj.teacher.id)
  teacher["name"] = "{} {}".format(teacher_obj.first_name, teacher_obj.last_name)
  teacher["grado"]= matricula.seccion.grado.name
  teacher["seccion"] = matricula.seccion.section
  teacher["seccion_has_name"] = matricula.seccion.name
  return teacher

def getWeeklyGradesForStudent( apoderado_id, ys_id, weeks, week, grading_info ):
  logger = logging.getLogger(__name__)
  students_grades = []
  teacher = {}
  logger.error(" apoderado_id: {}".format(apoderado_id))
  logger.error(Student.objects.filter(apoderado__id=apoderado_id))
  for s in Student.objects.filter(apoderado__id=apoderado_id):
    student = {}
    student["student_name"] = "{} {}".format(s.first_name, s.last_name)
    grades = []
    #FIXME: it could be possible that a student is registered in more than one class
    matricula = Matricula.objects.filter(yearsettings_id=ys_id,
            student_id=s.id).first()

    teacher = getTeacherInfo(ys_id, matricula)
    for idx, item in enumerate(weeks):
    #for sub in Subject.objects.filter(seccion_id=matricula.seccion_id):
      grade = {}
      has_grade = False
      if grading_info["has_simulacros"]:
        grade_obj = Grade.objects.filter(student_id=s.id, 
                subject_id__isnull=True, week=idx+1, grade_type=6).first()
        grade["simulacro"] = "-" if not grade_obj else grade_obj.grade
        if grade_obj:
          has_grade = True
      grade["week"] = idx+1
      if has_grade:
        grades.append(grade)
    student["grades"] = grades
    students_grades.append(student)
    #TODO: implement template for multiple students
    break
  return teacher, students_grades

def saveWeeklyGradesForSubject( params, week):
  #grades = Grade.objects.filter(subject_id=subject_id)
  for (k,v) in params.items():
    logger = logging.getLogger(__name__)
    logger.error("k: {}, v:{}".format(k,v))
    try:
      v = int(v)
    except:
      continue
    if k[0]=='u':
      student_id = k[1:]
      g = Grade.objects.filter(student_id=student_id, 
              subject_id__isnull=True, 
              grade_type=6,
              week=week).first()
      if v>=0:
        if not g:
          g = Grade(student_id=student_id, 
                  #subject_id__isnull=True, 
                  week=week, 
                  grade_type=6, 
                  grade=v)
        else:
          g.grade = v
        g.save()
      else:
        g.delete()
  return student_id

def getWeeklyGradesBySubjectForTeacher( teacher_id, ys_id, week ):
  logger = logging.getLogger(__name__)

  user = User.objects.get(id=teacher_id)
  grades = []
  teacher = {}
  tutor = Tutor.objects.get(teacher_id=user.id, year_id=ys_id)
  teacher["grado"] = tutor.seccion.grado.name
  teacher["seccion"] = tutor.seccion.section
  teacher["seccion_has_name"] = tutor.seccion.name
  #for sub in Subject.objects.filter(seccion_id=tutor.seccion.id).order_by('id'):
  grade = {}
  #grade["subject_name"] = sub.name
  #grade["subject_id"] = sub.id
  grade["week"] = week
  grade["student"] = []
  for m in Matricula.objects.filter(seccion_id=tutor.seccion.id, yearsettings_id=ys_id).order_by('student__last_name'):
    student = Student.objects.get(id=m.student_id)
    logger.error(student)
    c = Grade.objects.filter(student_id=student.id, 
            subject_id__isnull=True,
            #subject_id=sub.id, 
            grade_type=6,
            week=week).first()
    grade["student"].append(
            { 
              "student_id": student.id,
              "name": student.first_name + " " + student.last_name, 
              "simulacro": "-" if not c else c.grade, 
              "week": "-" if not c else c.week,
            })
  grades.append(grade)
  #data["cursos"] = cursos
  #data["students"] = students
  #[
  #        { "subject_name" : "matematica",
  #          "subject_id": "3",
  #          "notas": [
  #              "student_id": 2,
  #              "name": "juanito",
  #              "tarea": "30",
  #              "evaluacion": "-",
  #              "date": "03/04/2019",
  #          ]
  #        },
  #]
  return teacher, grades

def getReportForTeacher(teacher_id, ys_id, periods, period, grading_info):
  class_info = {}
  merito = {}
  tutor = Tutor.objects.get(teacher_id=teacher_id, year_id=ys_id)
  class_info["grado"] = tutor.seccion.grado.name
  class_info["seccion"] = tutor.seccion.section
  class_info["seccion_has_name"] = tutor.seccion.name
  grades = getAprobadosPercentage(teacher_id, ys_id, periods, period, grading_info)
  merito = getMerito(teacher_id, ys_id, periods, period, grading_info)
  return class_info, grades, merito

def getMerito(teacher_id, ys_id, periods, period, grading_info):
  list_merito = []
  tutor = Tutor.objects.get(teacher_id=teacher_id, year_id=ys_id)
  for matricula in Matricula.objects.filter(seccion_id=tutor.seccion.id, yearsettings_id=ys_id).order_by('student__last_name'):
    student = Student.objects.get(id=matricula.student_id)
    merito = {}
    avg = 0
    count = 0
    has_grades_in_all_subjects = True
    for subject in Subject.objects.filter(seccion_id=tutor.seccion.id).order_by('id'):
      g = computeMonthlyAverageGrade(student, subject, periods, period, grading_info)
      if g["pm"] == "-":
        has_grades_in_all_subjects = False
        break
      avg += float(g["pm"])
      count += 1
    if has_grades_in_all_subjects:
      merito["first_name"] = student.first_name
      merito["last_name"] = student.last_name
      merito["average"] = avg/count
      list_merito.append(merito)
  list_merito.sort(key=lambda x: x["average"])
  return list_merito
      
def getAprobadosPercentage(teacher_id, ys_id, periods, period, grading_info):
  grades = []
  tutor = Tutor.objects.get(teacher_id=teacher_id, year_id=ys_id)
  for subject in Subject.objects.filter(seccion_id=tutor.seccion.id).order_by('id'):
    grade = {}
    grade["subject_name"] = subject.name
    aprobados = 0
    desaprobados = 0
    everyone_has_grades = True
    for matricula in Matricula.objects.filter(seccion_id=tutor.seccion.id, yearsettings_id=ys_id).order_by('student__last_name'):
      student = Student.objects.get(id=matricula.student_id)
      g = computeMonthlyAverageGrade(student, subject, periods, period, grading_info)
      if g["pm"] == "-":
        everyone_has_grades = False 
        break
      if float(g["pm"]) >= 11:
        aprobados += 1
      else:
        desaprobados += 1
    if not everyone_has_grades:
      grade["aprobados"] = "-"
      grade["desaprobados"] = "-"
    else:
      grade["aprobados"] = aprobados*100.0/(aprobados+desaprobados)
      grade["desaprobados"] = desaprobados*100.0/(aprobados+desaprobados)
    grades.append(grade)
    return grades
