from datetime import datetime
from datetime import timedelta
from .models import YearSettings, Student, Matricula, Tutor
import logging, math

# get the user role, name and default date
class SetupFractal:
  def __init__(self, get_response):
    # One-time configuration and initialization
    self.get_response = get_response

  def setRequestUserRole(self, request):
    request.is_student = False
    request.is_teacher = False
    request.is_admin   = False
    if request.user.groups.filter(name='apoderado').exists():
      request.is_student = True
    elif request.user.groups.filter(name='teacher').exists():
      request.is_teacher = True
    elif request.user.is_superuser:
      request.is_admin = True

  def setRequestUserName(self, request):
    if not request.user.is_anonymous:
      request.user_name = "{} {}".format(request.user.first_name, request.user.last_name)

  def setRequestDayWeekMonthGrades(self, request):
    logger = logging.getLogger(__name__)
    request.has_daily_grades = False
    request.has_weekly_grades = False
    request.has_monthly_grades = False

    request.has_dailyeval_grade = False
    request.has_homeworks = False
    request.has_notebook_grade = False
    request.has_monthly_exam = False
    request.has_bimonthly_grade = False
    request.has_simulacros = False

    if request.is_student:
      student = Student.objects.filter(apoderado_id=request.user.id).first()
      grado = Matricula.objects.filter(yearsettings_id=request.year_id,
                                       student_id=student.id).first().seccion.grado
      request.has_dailyeval_grade = grado.has_dailyeval_grade
      request.has_homeworks = grado.has_homeworks
      request.has_notebook_grade = grado.has_notebook_grade
      request.has_monthly_exam = grado.has_monthly_exam
      request.has_bimonthly_grade = grado.has_bimonthly_grade
      request.has_simulacros = grado.has_simulacros
      if grado.has_homeworks or grado.has_dailyeval_grade:
        request.has_daily_grades = True
      if grado.has_simulacros:
        request.has_weekly_grades = True
      if grado.has_monthly_exam or grado.has_notebook_grade:
        request.has_monthly_grades = True

    elif request.is_teacher:
      tutor_obj = Tutor.objects.get(teacher_id=request.user.id)
      grado = tutor_obj.seccion.grado
      request.has_dailyeval_grade = grado.has_dailyeval_grade
      request.has_homeworks = grado.has_homeworks
      request.has_notebook_grade = grado.has_notebook_grade
      request.has_monthly_exam = grado.has_monthly_exam
      request.has_bimonthly_grade = grado.has_bimonthly_grade
      request.has_simulacros = grado.has_simulacros
      if grado.has_homeworks or grado.has_dailyeval_grade:
        request.has_daily_grades = True
      if grado.has_simulacros:
        request.has_weekly_grades = True
      if grado.has_monthly_exam or grado.has_notebook_grade:
        request.has_monthly_grades = True

    request.grading_info = {
      "has_dailyeval_grade" : request.has_dailyeval_grade,
      "has_homeworks"       : request.has_homeworks,
      "has_notebook_grade"  : request.has_notebook_grade,
      "has_monthly_exam"    : request.has_monthly_exam,
      "has_bimonthly_grade" : request.has_bimonthly_grade,
      "has_simulacros"      : request.has_simulacros
    } 

    logger.error("has daily grades {}".format(request.has_daily_grades))
    logger.error("has weekly grades {}".format(request.has_weekly_grades))
    logger.error("has monthly grades {}".format(request.has_monthly_grades))

  def __call__(self, request):
    # Code to be executed for each request before
    # the view (and later moddleware) are called.
    logger = logging.getLogger(__name__)

    # set user role
    self.setRequestUserRole(request)

    # set user_name
    self.setRequestUserName(request)

    # set request's date
    try:
      #datetime.strptime("2019-12-01", "%Y-%m-%d")
      if request.method == "POST":
        req_date = request.POST.get("date")
      elif request.method == "GET":
        req_date = request.GET.get("date")
      date_obj = datetime.strptime(req_date, "%Y-%m-%d")
      request.year_id = YearSettings.objects.filter(year=date_obj.year).first().id
      request.date = date_obj.strftime("%Y-%m-%d")
    except:
      today = datetime.now()
      request.year_id = YearSettings.objects.filter(year=today.year).first().id
      request.date = today.strftime("%Y-%m-%d")

    # set allowed day: sundays and holidays aren't allowed!
    request.is_allowed_day = True
    ys_obj = YearSettings.objects.filter(id=request.year_id).first()
    if request.is_student:
      student = Student.objects.filter(apoderado_id=request.user.id).first()
      grado = Matricula.objects.filter(yearsettings_id=request.year_id,
                                       student_id=student.id).first().seccion.grado
      request.is_saturday_allowed = grado.is_saturday_allowed
      logger.error("is saturday allowed {}".format(request.is_saturday_allowed))
      
    date_obj = datetime.strptime(request.date, "%Y-%m-%d")
    if date_obj.weekday()==6:
      request.is_allowed_day = False
    if request.is_student:
      if not grado.is_saturday_allowed and date_obj.weekday()==5:
        request.is_allowed_day = False
    if request.is_allowed_day:
      #FIXME: not very efficient, probably should be done only when loging in
      for holiday in YearSettings.objects.get(id=request.year_id).holidays:
        if date_obj.date() == holiday:
          request.is_allowed_day = False
          break
    logger.info("{} is allowed day? {}".format(request.date, request.is_allowed_day))

    # set daily, weekly and monthly booleans
    self.setRequestDayWeekMonthGrades(request)

    # set request's week
    try:
      if request.method == "POST":
        week = request.POST.get("week")
      elif request.method == "GET":
        week = request.GET.get("week")
      if week:
        request.week = int(week)
      else:
        request.week = 1 
    except:
      # FIXME: the default should be the current one
      request.week=1
    logger.error("week set to {}".format(request.week))

    # set current period
    try:
      if request.method == "POST":
        period = request.POST.get("period")
      elif request.method == "GET":
        period = request.GET.get("period")
      logger.error("period set to {}".format(period))
      if period:
        request.period = int(period)
      else:
        request.period = 1 
    except:
      # FIXME: the default should be the current one
      request.period=1
      
    #request.periods=[1,2,3,4,5,6,7,8]
    # Counting the weeks, period grades come every 5 weeks
    ys_obj = YearSettings.objects.get(id=request.year_id)
    delta = ys_obj.end_date - ys_obj.start_date
    weeks = math.ceil(delta.days/7)
    weeks_per_period = 5      # TODO: should be in db?
    num_periods = int(weeks/weeks_per_period)
    #periods = [
    #        { "start": "2019-03-04", "end" : "2019-04-06" },
    #        { "start": "2019-04-08", "end" : "2019-05-11" },
    #        { "start": "2019-05-13", "end" : "2019-06-15" },
    #        { "start": "2019-06-17", "end" : "2019-07-20" },
    #        { "start": "2019-08-05", "end" : "2019-09-07" },
    #        { "start": "2019-09-09", "end" : "2019-10-12" },
    #        { "start": "2019-10-14", "end" : "2019-11-16" },
    #        { "start": "2019-11-18", "end" : "2019-12-14" },
    #        ]              
    request.periods = ys_obj.periods

    #weeks = [ 
    #  { "start": "2019-06-17", "end": "2019-06-22" }, 
    #  { "start": "2019-06-24", "end": "2019-06-29" }, 
    #]
    weeks = []
    delta = timedelta(days=7)
    for period in ys_obj.periods:
      counter_date = datetime.strptime(period["start"], "%Y-%m-%d")
      end_period   = datetime.strptime(period["end"],   "%Y-%m-%d")
      while counter_date < end_period:
        str_week_start = datetime.strftime(counter_date, "%Y-%m-%d")
        str_week_end = datetime.strftime(counter_date + timedelta(days=5), "%Y-%m-%d")
        weeks.append( { "start": str_week_start, "end": str_week_end } )
        counter_date = counter_date + timedelta(days=7)


    logger.error( "weeks {}".format(weeks)) 
    request.weeks = weeks
    #for period in ys_obj.periods:
      
    logger.error( "periods!!: " )
    logger.error( request.periods )
    # TODO: add the period's dates
    #for p in num_periods:
    #  start_date = 
    #  periods.append({ 'start_date': start_date, 'end_date': end_date })

    # set current bimonth
    try:
      if request.method == "POST":
        bimonth = request.POST.get("bimonth")
      elif request.method == "GET":
        bimonth = request.GET.get("bimonth")
      logger.error("bimonth set to {}".format(bimonth))
      if bimonth:
        request.bimonth = int(bimonth)
      else:
        request.bimonth = 1 
    except:
      # FIXME: the default should be the current one
      request.bimonth=1

    #######################################################
    response = self.get_response(request) # This is the thing!

    # Code to be executed for each request/response after
    # the view is called.

    return response
