# -*- coding: utf-8 -*-
from django.test import TestCase
from asistencia.models import YearSettings, Grado, Seccion, ApoderadoUser, Student, Matricula
from .models import PaymentSettings, Payment
from .logic import getUserPaymentStatus

from freezegun import freeze_time

# Create your tests here.
class BillingTest(TestCase):
  def setUp(self):
    self.populate_db()

  def populate_db(self):
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
    cto_a = Seccion.objects.create(section='A', name="", grado=cuarto)
    apod1 = ApoderadoUser.objects.create(dni=11111101,
            first_name = "Apoderado",
            last_name = "1",
            username = "apod1")
    apod2 = ApoderadoUser.objects.create(dni=11111101,
            first_name = "Apoderado",
            last_name = "2",
            username = "apod2")
    stude1 = Student.objects.create(dni=22222201,
            first_name = "Estudiante",
            last_name = "1",
            apoderado = apod1)
    stude2 = Student.objects.create(dni=22222201,
            first_name = "Estudiante",
            last_name = "2",
            apoderado = apod2)
    matricula1 = Matricula.objects.create(yearsettings = year,
            student = stude1,
            seccion = cto_a)
    matricula2 = Matricula.objects.create(yearsettings = year,
            student = stude2,
            seccion = cto_a)
    PaymentSettings.objects.create(matricula = matricula1,
            matricula_amount = 400,
            monthly_amount = 300,
            has_promo = False)
    PaymentSettings.objects.create(matricula = matricula2,
            matricula_amount = 400,
            monthly_amount = 250,
            has_promo = True)
    
  #def test_all(self):

  def test_status_paid(self):
    expected_status = 1
    payment_settings = PaymentSettings.objects.get(id=1)
    Payment.objects.create(payment_date="2019-03-01",
            receipt_nro="123",
            payment_settings=payment_settings,
            pay_reference=0,
            amount=400)
    Payment.objects.create(payment_date="2019-03-02",
            receipt_nro="123",
            payment_settings=payment_settings,
            pay_reference=1,
            amount=300)
    Payment.objects.create(payment_date="2019-04-02",
            receipt_nro="123",
            payment_settings=payment_settings,
            pay_reference=2,
            amount=300)
    Payment.objects.create(payment_date="2019-05-02",
            receipt_nro="123",
            payment_settings=payment_settings,
            pay_reference=3,
            amount=300)

    user = ApoderadoUser.objects.get(id=1)
    freezer = freeze_time("2019-05-17 12:00:00")
    freezer.start()
    status = getUserPaymentStatus(user)
    freezer.stop()
    self.assertEqual(status, expected_status)

  def test_status_warning(self):
    expected_status = 2
    payment_settings = PaymentSettings.objects.get(id=1)
    Payment.objects.create(payment_date="2019-03-01",
            receipt_nro="123",
            payment_settings=payment_settings,
            pay_reference=0,
            amount=400)
    Payment.objects.create(payment_date="2019-03-02",
            receipt_nro="123",
            payment_settings=payment_settings,
            pay_reference=1,
            amount=300)
    Payment.objects.create(payment_date="2019-04-02",
            receipt_nro="123",
            payment_settings=payment_settings,
            pay_reference=2,
            amount=300)

    user = ApoderadoUser.objects.get(id=1)
    freezer = freeze_time("2019-05-12 12:00:00")
    freezer.start()
    status = getUserPaymentStatus(user)
    freezer.stop()
    self.assertEqual(status, expected_status)

  #def status_overdue(self):
  #  expected_status = 3
  #  user = ApoderadoUser.objects.get(id=1)
  #  status = getUserPaymentStatus(user)
  #  self.assertEqual(status, expected_status)

  #def status_paid_with_promo(self):
  #  expected_status = 1
  #  user = ApoderadoUser.objects.get(id=2)
  #  status = getUserPaymentStatus(user)
  #  self.assertEqual(status, expected_status)

  #def no_payment_settings(self):
  #  expected_status = 1
  #  user = ApoderadoUser.objects.get(id=2)
  #  status = getUserPaymentStatus(user)
  #  self.assertEqual(status, expected_status)
