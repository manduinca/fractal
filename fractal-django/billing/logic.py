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
  matricula = Matricula.objects.filter(student=student)
  payment_settings = PaymentSettings.objects.get(matricula=matricula)
  if payment_settings:
    required_amount = payment_settings.monthly_amount
    today = datetime.now()
    print(today.month)
    current_month = today.month
    payments = [ { "required": True, "paid": False, "pay_reference": 0 } ]
    # Load payment requirements
    for i in range(1, 11):
      required = True if today.month >= i+2 else False
      #payments[str(i)] = { "required": required , "paid": False }
      payments.append({ "required": required , "paid": False , "pay_reference": i })
    #payments=dict(sorted(payments.items(), key = lambda x:x[0]))
    print(payments)

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
    print(payments)

    # Now properly set the state!
    for idx, payment in enumerate(payments):
      # if this payment is required, but not paid set either 
      # warning or overdue, depending on the date!
      if payment["required"] and not payment["paid"]:
        if today.month >= int(idx+2):
          status = OVERDUE
        elif today.day >= 15:
          status = WARNING
      

  return status
