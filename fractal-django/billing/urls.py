from django.conf.urls import url

from . import views

urlpatterns = [
  url(r'^report/$', views.BillingReport.as_view(), name='billing_report'),
]
