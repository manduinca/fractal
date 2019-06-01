from asistencia.models import Matricula, Student
from .models import PaymentSettings, Payment
from datetime import datetime

# Returns the apoderadoUser status:
# 1: PAID (All paid so far)
# 2: WARNING (15 days after payment due)
# 3: OVERDUE (30 days after payment due)
def getUserPaymentStatus(user):
  PAID = 1
  WARNING = 2
  OVERDUE = 3
  status = PAID
  student = Student.objects.get(apoderado=user)
  matricula = Matricula.objects.get(student=student)
  payment_settings = PaymentSettings.objects.filter(matricula=matricula).first()
  if payment_settings:
    required_amount = payment_settings.monthly_amount
    today = datetime.now()
    current_month = today.month
    payments = [ { "required": True, "paid": False, "pay_reference": 0 } ]
    # Load payment requirements
    for i in range(1, 11):
      required = True if today.month >= i+2 else False
      payments.append({ "required": required , "paid": False , "pay_reference": i })
    #print(payments)

    # Load actual payments from DB
    for payment in Payment.objects.filter(payment_settings = payment_settings).order_by('pay_reference'):
      # Matricula has its own field, so special treatment
      paid = False
      if payment.pay_reference == 0:
        paid = True if payment.amount >= payment_settings.matricula_amount else False
      # Special treatment is has_promo
      elif payment.pay_reference==10 and payment_settings.has_promo:
        paid = True if payment.amount >= payment_settings.monthly_amount/2 else False
      # regular treatement
      else:
        paid = True if payment.amount >= payment_settings.monthly_amount else False
      payments[payment.pay_reference]["paid"] = paid
    #print(payments)

    # Now properly set the state!
    for idx, payment in enumerate(payments):
      # if this payment is required, but not paid set either 
      # warning or overdue, depending on the date!
      if payment["required"] and not payment["paid"]:
        #print(payment)
        if today.day <= 15:
          status = WARNING
        else:
          status = OVERDUE

  return status
