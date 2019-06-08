# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect
from django.views import generic
from django.utils.http import is_safe_url
from django.contrib.auth import authenticate
from django.contrib.auth import REDIRECT_FIELD_NAME, login as auth_login, logout as auth_logout

from django.http import HttpResponse
from reportlab.pdfgen import canvas

import csv
import logging
from unidecode import unidecode

from datetime import datetime

from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import AuthenticationForm
from .models import Asistencia, ApoderadoUser, Student, Schedule, YearSettings, Tutor, Subject, Matricula
from django.contrib.auth.models import User
from django import forms
from django.core.files.storage import FileSystemStorage
from .logic import saveGradesForSubject, getGradesBySubjectForTeacher, getGradesForStudent
from .logic import getWeeklyGradesForStudent, saveWeeklyGradesForSubject, getWeeklyGradesBySubjectForTeacher
from .logic import getMonthlyGradesBySubjectForTeacher, saveMonthlyGradesForSubject, getMonthlyGradesForStudent
from .logic import getBiMonthlyGradesForStudent, getBiMonthlyGradesByStudentForTeacher
from .logic import getFormatedSchedule
from .logic import getReportForTeacher

from billing.logic import getAdminReport
# Create your views here.

# This is just for login and redirect properly
#class IndexView(LoginRequiredMixin, generic.ListView):
#  login_url = '/login'
#  redirect_field_name = 'redirect_to'
#  def logout_view
  
# https://coderwall.com/p/sll1kw/django-auth-class-based-views-login-and-logout
# FIXME: the initial redirect should be according to the user role
class LoginAsistenciaView(generic.FormView):
  #template_name = 'asistencia/login.html'
  success_url = '/asistencias/'
  template_name = 'asistencia/login.html'
  form_class = AuthenticationForm
  redirect_field_name = REDIRECT_FIELD_NAME

  @method_decorator(sensitive_post_parameters('password'))
  @method_decorator(csrf_protect)
  @method_decorator(never_cache)
  def dispatch(self, request, *args, **kwargs):
  # Sets a test cookie to make sure the user has cookies enabled
    request.session.set_test_cookie()
    return super(LoginAsistenciaView, self).dispatch(request, *args, **kwargs)

  def form_valid(self, form):
    auth_login(self.request, form.get_user())
    # If the test cookie worked, go ahead and
    # delete it since its no longer needed
    if self.request.session.test_cookie_worked():
      self.request.session.delete_test_cookie()

    return super(LoginAsistenciaView, self).form_valid(form)

  def get_success_url(self):
    #redirect_to = self.request.REQUEST.get(self.redirect_field_name)
    redirect_to = self.request.GET.get(self.redirect_field_name)
    if not is_safe_url(url=redirect_to, host=self.request.get_host()):
      redirect_to = self.success_url
    return redirect_to
  #def get(self, request, *args, **kwargs):
  #  return render(request, self.template_name, {})

  #def post(self, request, *args, **kwargs):
  #  user = authenticate(

class LogoutAsistenciaView(generic.RedirectView):
  url = '../login/'
  def get(self, request, *args, **kwargs):
    auth_logout(request)
    #return super(LogoutView, self).get(request, *args, **kwargs) 
    return super(LogoutAsistenciaView, self).get(request, *args, **kwargs) 

# This is the daily attendance
class AsistenciaListView(LoginRequiredMixin, generic.ListView):
#class AsistenciaListView(generic.ListView):
  #login_url = 'asistencias/login'
  login_url = 'login/'
  redirect_field_name = 'redirect_to'
  model = Asistencia
  #aname = Asistencia.student.apoderado
  ## Assuming only apoderados and not teachers!
  ## for that create a middleware to handle that
  #aname = get_queryset(self)
  sname = Asistencia.student
  template_name = 'asistencia/asistencia_list.html'
  #sdni = Asistencia.student.dni
  def get(self, request, *args, **kwargs):
    #logger = logging.getLogger()
    #logger.debug(request.user)
    aname = ApoderadoUser.objects.filter(id=request.user.id).first()
    # FIXME: not the best way to make the redirect =/
    #if request.user.groups.filter(name='apoderado').exists():
    if request.is_student:
      group = "apoderado"
    elif request.is_teacher:
      group = "teacher"
      if request.has_daily_grades:
        return redirect("grading_daily")
      elif request.has_weekly_grades:
        return redirect("grading_weekly")
      elif request.has_monthly_grades:
        return redirect("grading_monthly")
    #elif request.user.groups.filter(name='profesor').exists():
    #  group = "profesor"
    elif request.is_admin:
      group = "admin"
      #return redirect(UploadFileForm.as_view())
      return redirect("upload_asis")

    #aname = ApoderadoUser(request.user)
    #FIXME: Always getting the first!
    s = Student.objects.filter(apoderado=request.user).first()
    s_names=""
    a = '['
    f = '['
    horaEntrada = Matricula.objects.filter(student=s).first().seccion.grado.entrada.strftime("%H:%M")
    sname = "{} {}".format(s.first_name, s.last_name)
    sdni = s.dni
    asistencias = Asistencia.objects.filter(student=s).order_by("hour")
    for asistencia in asistencias:
      a = a + "'" + asistencia.hour.strftime("%Y-%m-%dT%H:%M:%S") + "',"


    a = a + ']'
    f = f + ']'
    #a = '[ "2018-05-01", "2018-05-02", "2018-05-03" ]'
    #f = "[ '2018-05-04', '2018-05-05', '2018-05-06' ]"
    #return render(request, self.template_name, {'apoderado':aname, 'asistencias': a, 'faltas': f , 'students': s_names})
    year=YearSettings.objects.get(year=datetime.now().year)
    return render(request, self.template_name, 
            {
                'apoderado':aname, 
                'asistencias': a, 
                'faltas': f, 
                'sname': sname, 
                'sdni':sdni, 
                'hora_entrada': horaEntrada, 
                'start_date': year.start_date.strftime("%Y-%m-%d")
            })
    #return render(request, self.template_name, {'apoderado':self.aname, 'sname':self.sname})
  #def post(self, request, *args, **kwargs):
  #def get_queryset(self):
  #  return ApoderadoUser.objects.filter(user=self.request.user)
    
  #template_name = 'asistencia/asistencias_list.html'
#class AsistenciaView(generic.DetailView):
#  model = Asistencia

# This class is to show the subjects schedule
class ScheduleListView(LoginRequiredMixin, generic.ListView):
  login_url = 'login/'
  redirect_field_name = 'redirect_to'
  template_name = 'asistencia/asistencia_schedule.html'
  model = Asistencia
  sname = Asistencia.student
  def get(self, request, *args, **kwargs):
    students = Student.objects.filter(apoderado=request.user)
    if len(students) > 0:
      s = students[0]
      #grado = Matricula.objects.filter(yearsettings_id=request.year_id,
      #                                 student_id=s.id).first().seccion
      #grado = s.grado
      section = Matricula.objects.filter(yearsettings_id=request.year_id,
                                       student_id=s.id).first().seccion
      grado = section.grado
      subjects = Subject.objects.filter(seccion_id=section.id)
      #for s in subjects:

      schedule = []
      row_0 = ["07:45 - 08:00"]
      number_of_days = 5 if not request.is_saturday_allowed else 6
      for i in range(0,number_of_days):
        row_0.append("Formacion")
      schedule.append(row_0)
      rows = getFormatedSchedule(request.user.id, request.year_id, request.is_saturday_allowed )
      for r in rows:
        schedule.append(r)
      logger = logging.getLogger(__name__)
      logger.error(schedule)
      return render(request, self.template_name, {'schedule':schedule, 'grado':grado.grado, 'seccion':section, 'num_cols': number_of_days})
    #schedule = '[ \
    #  ["07:45 - 08:00", "Formacion", "Formacion", "Formacion", "Formacion", "Formacion"],\
    #  ["08:00 - 09:00", "Quimica", "Educ. Fisica", "Geometria", "Raz. Mat.", "Biologia"],\
    #  ["09:00 - 10:00", "Quimica", "Educ. Fisica", "Geometria", "Raz. Mat.", "Biologia"],\
    #  ["10:15 - 11:15", "Fisica", "Lenguaje", "Aritmetica", "Tutoria", "Algebra"],\
    #  ["11:15 - 12:15", "Fisica", "Lenguaje", "Aritmetica", "H. del Peru", "Algebra"],\
    #  ["12:35 - 01:35", "Trigonometria", "Literatura", "Ingles", "H. del Peru", "H. Universal"],\
    #  ["01:35 - 02:35", "Trigonometria", "Literatura", "Ingles", "Geografia", "H. Universal"],\
    #  ["02:35 - 02:45", "Entr. Cuad.","Entr. Cuad.","Entr. Cuad.","Entr. Cuad.","Entr. Cuad."],\
    #]'


    return render(request, self.template_name, {'schedule':'[]'})

# https://docs.djangoproject.com/en/1.11/topics/http/file-uploads/
class FileFieldForm(forms.Form):
  #title = forms.CharField(max_length=50)
  file_field = forms.FileField(error_messages={'required': 'Se necesita enviar un archivo'})

# https://simpleisbetterthancomplex.com/tutorial/2016/08/01/how-to-upload-files-with-django.html
class UploadFileForm(LoginRequiredMixin, generic.FormView):
  login_url = '../login/'
  redirect_field_name = 'redirect_to'

  form_class = FileFieldForm
  template_name = "asistencia/upload_asistencia.html"
  success_url = './'

  #def get(self, request, *args, **kwargs):
  #  if request.is_student:
  #    return redirect ("asistencias_list")
  #  elif request.is_teacher:
  #    return redirect ("grading_daily")
  #  get(request)
  #  return render(request, self.template_name, {} )

  def post(self, request, *args, **kwargs):
    if request.is_student:
      return redirect ("asistencias_list")
    elif request.is_teacher:
      return redirect ("grading_daily")
    #if request.user.groups.filter(name='apoderado').exists():
    #  redirect ( "asistencias_list")
    form_class = self.get_form_class()
    form = self.get_form(form_class)
    #files = request.FILES.getlist('file_field')
    files = request.FILES.getlist('file_field')
    #msg = len(files)
    msg = ""
    if form.is_valid():
      for file in files:
        fs = FileSystemStorage()
        filename = fs.save(file.name, file)
        #msg = fs.url(filename)
        with open("." + fs.url(filename)) as f:
        #for f in file.chunks():
          #r = csv.reader(f, delimiter=str(u';').encode('utf-8'), quotechar='|')
          #r = csv.reader(f, delimiter=str(u'\t').encode('utf-8'), quotechar=str(u'|').encode('utf-8'))
          #r = csv.reader(f, delimiter=str(u'\t').encode('utf-8'))
          r = csv.reader(f, delimiter=str("\t"))
          for line in r:
             dni = line[0]
             date = line[1]
             res = Student.objects.filter(dni=dni)
             #s = Student.objects.get(dni=int(dni))
             if len(res) == 0: #skip non-existing DNIs
               continue
             s = res[0]
             if Asistencia.objects.filter(student=s, hour=date).count() > 0: #skip repeated
               continue
             a = Asistencia(student=s, hour=date)
             #msg += dni + "," + s.first_name +"," + a.hour.strftime("%d-%m-%Y") + "<br>\n"
             a.save()
             msg += dni + "," + s.first_name +"," + a.hour + "<br>\n"
             #msg = "Asistencias procesadas correctamente, de haber DNIs no registrados en el sistema seran ignorados"
      msg = "Asistencias procesadas correctamente, de haber DNIs no registrados en el sistema seran ignorados"
      #return self.form_valid(form)
      return render(request, self.template_name, {'error_msg':msg})
    else:
      return render(request, self.template_name, {'error_msg':"error"})
      #return self.form_invalid(form) 

class GradingListView(LoginRequiredMixin, generic.ListView):
  login_url = 'login/'
  redirect_field_name = 'redirect_to'
  template_name = 'asistencia/grading/daily.html'

  def get(self, request, *args, **kwargs):
    logger = logging.getLogger(__name__)
    #logger.error(request.content_params)
    if request.is_student:
      teacher, grades = getGradesForStudent(request.user.id, request.year_id, request.date, request.grading_info )
    elif request.is_teacher:
      is_teacher = True
      #data = getGradesByStudentForTeacher(request.user.id, request.year_id)
      teacher, grades = getGradesBySubjectForTeacher(request.user.id, request.year_id, request.date)

    logger.error(grades)
    return render(request, self.template_name, 
            {
              'teacher': teacher,
              'grades' : grades,
              'msg' : ''
            })

  def post(self, request, *args, **kwargs):
    logger = logging.getLogger(__name__)
    data = {}
    if request.is_student:
      logger.error("student shouldn't be posting, are you trying to hack us?")
    elif request.is_teacher:
      saveGradesForSubject(request.POST.get("subject"), request.POST, request.date)
      teacher, grades = getGradesBySubjectForTeacher(request.user.id, request.year_id, request.date)

    return render(request, self.template_name, 
            {
              'teacher': teacher,
              'grades' : grades,
              'msg' : ''
            })

class MonthlyGradingListView(LoginRequiredMixin, generic.ListView):
  login_url = 'login/'
  redirect_field_name = 'redirect_to'
  template_name = 'asistencia/grading/monthly.html'

  def get(self, request, *args, **kwargs):
    logger = logging.getLogger(__name__)
    #logger.error(request.content_params)
    if request.is_student:
      teacher, grades = getMonthlyGradesForStudent(request.user.id, request.year_id, request.periods, request.period, request.grading_info )
    elif request.is_teacher:
      teacher, grades = getMonthlyGradesBySubjectForTeacher(request.user.id, request.year_id, request.period, request.grading_info )

    logger.error(grades)
    return render(request, self.template_name, 
            {
              'teacher': teacher,
              'grades' : grades,
              #'active' : grades[0]["subject_id"],
              'msg' : ''
            })

  def post(self, request, *args, **kwargs):
    logger = logging.getLogger(__name__)
    data = {}
    active = 1
    if request.is_student:
      logger.error("student shouldn't be posting, are you trying to hack us?")
    elif request.is_teacher:
      active = saveMonthlyGradesForSubject(request.POST.get("subject"), request.POST, request.period)
      teacher, grades = getMonthlyGradesBySubjectForTeacher(request.user.id, request.year_id, request.period, request.grading_info)

    logger.error("active {}".format(active))
    return render(request, self.template_name, 
            {
              'teacher': teacher,
              'grades' : grades,
              'active' : active,
              'msg' : ''
            })

class BiMonthlyGradingListView(LoginRequiredMixin, generic.ListView):
  login_url = 'login/'
  redirect_field_name = 'redirect_to'
  template_name = 'asistencia/grading/bimonthly.html'

  def get(self, request, *args, **kwargs):
    logger = logging.getLogger(__name__)
    #logger.error(request.content_params)
    if request.is_student:
      teacher, grades = getBiMonthlyGradesForStudent(request.user.id, request.year_id, request.periods, request.bimonth, request.grading_info)
    elif request.is_teacher:
      student_id = request.GET.get("student_id")
      if not student_id:
        student_id = -1
      else:
        student_id = int(student_id)
      class_info, students, grades_for_student = getBiMonthlyGradesByStudentForTeacher(request.user.id, request.year_id, student_id, request.periods, request.bimonth, request.grading_info )
      return render(request, self.template_name,
              {
                "class_info": class_info,
                "students"  : students,
                "grades"    : grades_for_student
              })

    logger.error(grades)
    return render(request, self.template_name, 
            {
              'teacher': teacher,
              'grades' : grades,
              'msg' : ''
            })

  #def post(self, request, *args, **kwargs):
  #  logger = logging.getLogger(__name__)
  #  data = {}
  #  active = 1
  #  if request.is_student:
  #    logger.error("student shouldn't be posting, are you trying to hack us?")
  #  elif request.is_teacher:
  #    active = saveMonthlyGradesForSubject(request.POST.get("subject"), request.POST, request.period)
  #    teacher, grades = getMonthlyGradesBySubjectForTeacher(request.user.id, request.year_id, request.period)

  #  logger.error("active {}".format(active))
  #  return render(request, self.template_name, 
  #          {
  #            'teacher': teacher,
  #            'grades' : grades,
  #            'active' : active,
  #            'msg' : ''
  #          })

class WeeklyGradingListView(LoginRequiredMixin, generic.ListView):
  login_url = 'login/'
  redirect_field_name = 'redirect_to'
  template_name = 'asistencia/grading/weekly.html'

  def get(self, request, *args, **kwargs):
    teacher = {}
    grades = {}
    if request.is_student:
      teacher, grades = getWeeklyGradesForStudent(request.user.id, request.year_id, request.weeks, request.week, request.grading_info )
    elif request.is_teacher:
      teacher, grades = getWeeklyGradesBySubjectForTeacher(request.user.id, request.year_id, request.week)
    return render(request, self.template_name, 
            {
              'teacher': teacher,
              'grades' : grades,
              'active' : 1,
              'msg' : ''
            })

  def post(self, request, *args, **kwargs):
    logger = logging.getLogger(__name__)
    data = {}
    active = 1
    if request.is_student:
      logger.error("student shouldn't be posting, are you trying to hack us?")
    elif request.is_teacher:
      active = saveWeeklyGradesForSubject(request.POST, request.week)
      teacher, grades = getWeeklyGradesBySubjectForTeacher(request.user.id, request.year_id, request.week)

    logger.error("active {}".format(active))
    return render(request, self.template_name, 
            {
              'teacher': teacher,
              'grades' : grades,
              'active' : active,
              'msg' : ''
            })

class ReportsListView(LoginRequiredMixin, generic.ListView):
  login_url = 'login/'
  redirect_field_name = 'redirect_to'
  template_name = 'asistencia/grading_reports.html'

  def get(self, request, *args, **kwargs):
    logger = logging.getLogger(__name__)
    class_info, grades, merito = getReportForTeacher(request.user.id, request.year_id, request.periods, request.period, request.grading_info)
    return render(request, self.template_name, 
            {
              'class_info': class_info,
              'grades'    : grades,
              'merito'    : merito
            })

#def getLibretas(request, student_id):
def getLibretas(request):
  logger = logging.getLogger(__name__)
  #logger.error( "getLibretas: student {}".format(student_id))
  if not request.is_teacher:
    return redirect("/asistencias/")
  if request.method != "GET":
    return redirect("/asistencias/")
  student_id = request.GET.get("student_id")
  if not student_id:
    student_id = -1
  student_id = int(student_id)
  class_info, students, grades_for_student = getBiMonthlyGradesByStudentForTeacher(request.user.id, request.year_id, student_id, request.periods, request.bimonth, request.grading_info )
  logger.error( "getLibretas: student {}".format(student_id))
  # Create the HttpResponse object with the appropriate PDF headers.
  response = HttpResponse(content_type='application/pdf')
  response['Content-Disposition'] = 'attachment; filename="libreta.pdf"'

  # Create the PDF object, using the response object as its "file."
  p = canvas.Canvas(response)
  
  # Draw things on the PDF. Here's where the PDF generation happens.
  # See the ReportLab documentation for the full list of functionality.
  #p.drawString(100, 100, "Hello world.")

  p.setFont("Helvetica", 20)
  p.drawCentredString(300, 780, "Institucion Educativa Fractal")
  p.setFont("Helvetica", 16)
  p.drawCentredString(300, 760, "Libreta de Notas")
  p.drawCentredString(300, 740, "Nivel: Educacion Secundaria")
  p.drawCentredString(300, 720, "Bimestre {}".format(request.bimonth))
  p.drawCentredString(300, 700, "{}, Seccion {}".format(class_info["grado"], class_info["seccion"]))
  p.setFont("Helvetica", 12)
  for student in students:
    if student["is_selected"]:
      p.drawCentredString(300, 680, "Estudiante: {}".format(student["student_name"]))
      break

  y = 640
  x_curso = 100
  x_grade = 250
  grades = {
      "matematica":   { "grade": 0, "subjects": [] },
      "comunicacion": { "grade": 0, "subjects": [] }, 
      "cta":          { "grade": 0, "subjects": [] }, 
      "ccss":         { "grade": 0, "subjects": [] }
    }
  data = [ ]
  for grade in grades_for_student:
    if unidecode(grade["subject_name"].lower()).find("geometria") >= 0:
      grades["matematica"]["subjects"].append(grade)
    elif unidecode(grade["subject_name"].lower()).find("trigonometria") >= 0:
      grades["matematica"]["subjects"].append(grade)
    elif unidecode(grade["subject_name"].lower()).find("algebra") >= 0:
      grades["matematica"]["subjects"].append(grade)
    elif unidecode(grade["subject_name"].lower()).find("aritmetica") >= 0:
      grades["matematica"]["subjects"].append(grade)
    elif unidecode(grade["subject_name"].lower()).find("razonamiento matem") >= 0:
      grades["matematica"]["subjects"].append(grade)
    elif unidecode(grade["subject_name"].lower()).find("lenguaje") >= 0:
      grades["comunicacion"]["subjects"].append(grade)
    elif unidecode(grade["subject_name"].lower()).find("literatura") >= 0:
      grades["comunicacion"]["subjects"].append(grade)
    elif unidecode(grade["subject_name"].lower()).find("razonamiento verbal") >= 0:
      grades["comunicacion"]["subjects"].append(grade)
    elif unidecode(grade["subject_name"].lower()).find("biolog") >= 0:
      grades["cta"]["subjects"].append(grade)
    elif unidecode(grade["subject_name"].lower()).find("fisica") == 0: # >= could be confused with educacion fisica
      grades["cta"]["subjects"].append(grade)
    elif unidecode(grade["subject_name"].lower()).find("quimica") >= 0:
      grades["cta"]["subjects"].append(grade)
    elif unidecode(grade["subject_name"].lower()).find("historia") >= 0:
      grades["ccss"]["subjects"].append(grade)
    elif unidecode(grade["subject_name"].lower()).find("geografia") >= 0:
      grades["ccss"]["subjects"].append(grade)
    else:
      grades[unidecode(grade["subject_name"].lower())] = { "grade": 0, "subjects": [ grade ] }
        
    #p.drawString(x_curso, y, grade["subject_name"])
    #p.drawString(x_grade, y, str(grade["pb"]))
    #y -= 20
  for area,areas in grades.items():
    grade = 0
    for subject in areas["subjects"]:
      if subject["pb"] != "-":
        grade += subject["pb"]
    #FIXME:subjects["grade"] = roundUp(grade/len(area["subjects"]))
    areas["grade"] = round(grade/len(areas["subjects"]))
      
  for area,areas in grades.items():
    if unidecode(area).find("tutoria") >= 0:
      continue
    p.setFillColorRGB(0.125, 0.386, 0.6)
    p.rect(x_curso-5, y-5, 150, 20, stroke=0, fill=1)
    p.setFillColorRGB(0,0,0)
    p.drawString(x_curso, y, area.capitalize())
    p.setFillColorRGB(0.125, 0.386, 0.6)
    p.rect(x_grade-5, y-5, 40, 20, stroke=0, fill=1)
    p.setFillColorRGB(0,0,0)
    p.drawString(x_grade, y, str(areas["grade"]))
    y -= 20
    if len(areas["subjects"]) <= 1:
      continue
    for subject in areas["subjects"]:
      p.drawString(x_curso, y, subject["subject_name"].capitalize())
      p.drawString(x_grade, y, str(subject["pb"]))
      y -= 20
  
  # Close the PDF object cleanly, and we're done.
  p.showPage()
  p.save()
  return response

class BillingReport(LoginRequiredMixin, generic.ListView):
  login_url = 'login/'
  redirect_field_name = 'redirect_to'
  template_name = 'billing/report.html'
  
  def get(self, request, *args, **kwargs):
    if request.is_student:
      return redirect ("asistencias_list")
    elif request.is_teacher:
      return redirect ("grading_daily")
    report = getAdminReport()
    return render(request, self.template_name, report)

  def post(self, request, *args, **kwargs):
    if request.is_student:
      return redirect ("asistencias_list")
    elif request.is_teacher:
      return redirect ("grading_daily")
    report = getAdminReport()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="reporte_pagos_{}.csv"'.format(report["report_date"])

    writer = csv.writer(response)
    writer.writerow(['Usuario', 'Monto', 'Concepto', 'Grado'])
    for payment in report["payments"]:
      if payment["pay_reference"] == 0:
        concept = "Matricula"
      elif payment["pay_reference"] == 1:
        concept  = "Marzo"
      elif payment["pay_reference"] == 2:
        concept  = "Abril"
      elif payment["pay_reference"] == 3:
        concept  = "Mayo"
      elif payment["pay_reference"] == 4:
        concept  = "Junio"
      elif payment["pay_reference"] == 5:
        concept  = "Julio"
      elif payment["pay_reference"] == 6:
        concept  = "Agosto"
      elif payment["pay_reference"] == 7:
        concept  = "Septiembre"
      elif payment["pay_reference"] == 8:
        concept  = "Octubre"
      elif payment["pay_reference"] == 9:
        concept  = "Noviembre"
      elif payment["pay_reference"] == 10:
        concept = "Diciembre"
      writer.writerow([ payment["user"], payment["amount"], concept, payment["grado"] ])

    return response
