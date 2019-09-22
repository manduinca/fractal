from django.conf.urls import url

from . import views

urlpatterns = [
  #url(r'^libretas/<int:student_id>/$', views.getLibretas, name='download_libretas'),
  url(r'^debtors_list/$', views.DebtorsList.as_view(), name='debtors_list'),
  url(r'^billing_report/$', views.BillingReport.as_view(), name='billing_report'),

  url(r'^libretas/$', views.getLibretas, name='download_libretas'),
  url(r'^reports/$', views.ReportsListView.as_view(), name='grading_reports'),
  url(r'^bimonthly/$', views.BiMonthlyGradingListView.as_view(), name='grading_bimonthly'),
  url(r'^monthly/$', views.MonthlyGradingListView.as_view(), name='grading_monthly'),
  url(r'^weekly/$', views.WeeklyGradingListView.as_view(), name='grading_weekly'),
  url(r'^daily/$', views.GradingListView.as_view(), name='grading_daily'),
  url(r'^payments/$', views.PaymentsView.as_view(), name='payments'),
  url(r'^incidents/$', views.IncidentsView.as_view(), name='incidents'),
  url(r'^schedule/$', views.ScheduleListView.as_view(), name='asistencias_schedule'),
  url(r'^uploadasis/$', views.UploadFileForm.as_view(), name='upload_asis'),
  url(r'^login/$', views.LoginAsistenciaView.as_view(), name='asistencias_login'),
  url(r'^logout/$', views.LogoutAsistenciaView.as_view(), name='asistencias_logout'),
  url(r'^$', views.AsistenciaListView.as_view(), name='asistencias_list'),

]
