from asistencia.models import Matricula, Student, ApoderadoUser
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

    # Now properly set the state: all payments so far must be done AND the see the situation for current month
    for idx, payment in enumerate(payments):
      if idx==today.month-2:
        break
      if payment["required"] and not payment["paid"]:
        status = OVERDUE
    if status!= OVERDUE and today.month >= 3 :
      payment = payments[today.month-2]
      # if this payment is required, but not paid set either 
      # warning or overdue, depending on the date!
      if payment["required"] and not payment["paid"]:
        #print(payment)
        if today.day <= 15:
          status = WARNING
        else:
          status = OVERDUE
      
  return status

# This is just for the admin user!
def getAdminReport():
  total_amount = 0
  total_paid_amount = 0
  total_debt_amount = 0
  payments = []         # by month
  debtor_users = []     # Only considers the ones in OVERDUE state
  not_configured_users_count = 0

  today = datetime.now()
  ps_count = 0
  for ps in PaymentSettings.objects.all():
    ps_count += 1
    month_count = today.month-2
    total_amount += month_count*ps.monthly_amount + ps.matricula_amount
    if ps.has_promo:
      total_amount -= ps.monthly_amount/2
    # TODO: Optimize. One way could be to add a payment_state field 
    # in the user table, so it's updated each time a payment is done and 
    # by a cronjob every 1st and 15th of the month at 01:00 local time
    user_status = getUserPaymentStatus(ps.matricula.student.apoderado)
    if user_status == 3:
        debtor_users.append({"username": ps.matricula.student.apoderado, "grado": ps.matricula.seccion} )
    for p in Payment.objects.filter(payment_settings=ps).order_by('payment_settings__matricula__seccion', 'pay_reference'):
      total_paid_amount += p.amount
      payments.append({ "user": ps.matricula.student.apoderado.username, 
                        "amount": p.amount, 
                        "pay_reference": p.pay_reference, 
                        "grado": ps.matricula.seccion
                        })
  not_configured_users_count = ApoderadoUser.objects.all().count() - ps_count
  total_debt_amount = total_amount - total_paid_amount
  return {
          "total_debt_amount": total_debt_amount,
          "payments"         : payments,
          "debtors"          : debtor_users,
          "no_config_users"  : not_configured_users_count,
          "report_date"      : today.strftime("%Y-%m-%d")
          }
