from django.shortcuts import render
from billing.logic import getAdminReport

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic

from django.http import HttpResponse

import csv

# Create your views here.
class BillingReport(LoginRequiredMixin, generic.ListView):
  login_url = 'login/'
  redirect_field_name = 'redirect_to'
  template_name = 'billing/report.html'
  
  def get(self, request, *args, **kwargs):
    report = getAdminReport()

    return render(request, self.template_name, report)

  def post(self, request, *args, **kwargs):
    report = getAdminReport()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="reporte_pagos_{}.csv"'.format(report["report_date"])

    writer = csv.writer(response)
    writer.writerow(['Usuario', 'Monto', 'Concepto', 'Grado'])
    for payment in report["payments"]:
      if payment["pay_reference"] == 0:
        concept = "Matricula"
      elif payment["pay_reference"] == 1:
        cept = "Marzo"
      elif payment["pay_reference"] == 2:
        cept = "Abril"
      elif payment["pay_reference"] == 3:
        cept = "Mayo"
      elif payment["pay_reference"] == 4:
        cept = "Junio"
      elif payment["pay_reference"] == 5:
        cept = "Julio"
      elif payment["pay_reference"] == 6:
        cept = "Agosto"
      elif payment["pay_reference"] == 7:
        cept = "Septiembre"
      elif payment["pay_reference"] == 8:
        cept = "Octubre"
      elif payment["pay_reference"] == 9:
        cept = "Noviembre"
      elif payment["pay_reference"] == 10:
        concept = "Diciembre"
      writer.writerow([ payment["user"], payment["amount"], concept, payment["grado"] ])

    return response
