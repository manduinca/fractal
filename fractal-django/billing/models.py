from django.db import models
from asistencia.models import Matricula

from django.utils import timezone

# Create your models here.
class PaymentSettings(models.Model):
  matricula = models.ForeignKey(Matricula, on_delete=models.CASCADE)
  matricula_amount = models.DecimalField("Monto de la Matricula", max_digits=6, decimal_places=2)
  monthly_amount = models.DecimalField("Monto de la Mensualidad", max_digits=6, decimal_places=2, default=300.00)
  has_promo = models.BooleanField("Tiene promocion?", default=False)
  REF_CHOICES = (
          (1, "Marzo"),
          (2, "Abril"),
          (3, "Mayo"),
          (4, "Junio"),
          (5, "Julio"),
          (6, "Agosto"),
          (7, "Septiembre"),
          (8, "Octubre"),
          (9, "Noviembre"),
          (10, "Diciembre"),
          )
  first_month = models.IntegerField("Primer mes de pago", choices=REF_CHOICES, default=1)
  
  class Meta:
    verbose_name = "Configuracion de pagos"
    verbose_name_plural = "Configuraciones de pagos"
  def __unicode__(self):
    return "{} {}".format(self.matricula, self.monthly_amount)
  def __str__(self):
    return "{} {}".format(self.matricula, self.monthly_amount)

class Payment(models.Model):
  payment_date = models.DateField("Fecha de pago", default=timezone.now)
  receipt_nro = models.IntegerField("Numero de recibo")
  payment_settings = models.ForeignKey(PaymentSettings, on_delete=models.CASCADE)
  REF_CHOICES = (
          (0, "Matricula"),
          (1, "Marzo"),
          (2, "Abril"),
          (3, "Mayo"),
          (4, "Junio"),
          (5, "Julio"),
          (6, "Agosto"),
          (7, "Septiembre"),
          (8, "Octubre"),
          (9, "Noviembre"),
          (10, "Diciembre"),
          )
  pay_reference = models.IntegerField("Concepto", choices=REF_CHOICES)
  amount = models.DecimalField("Monto", max_digits=6, decimal_places=2)

  class Meta:
    verbose_name = "Pago"
    verbose_name_plural = "Pagos"
  def __unicode__(self):
    return "{} {}".format(self.receipt_nro, self.amount)
  def __str__(self):
    return "{} {}".format(self.receipt_nro, self.amount)
