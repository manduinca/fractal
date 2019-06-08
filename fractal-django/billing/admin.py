from django.contrib import admin

from .models import PaymentSettings, Payment
# Register your models here.

class PaymentSettingsAdmin(admin.ModelAdmin):
  list_display = ( 'matricula', 'matricula_amount', 'monthly_amount', 'has_promo', 'apoderado' )
  list_display_links = ( 'apoderado', )
  #search_fields = [ 'matricula', ]
  list_filter = ( 'matricula__seccion', )
  def apoderado(self, obj):
    return obj.matricula.student.apoderado.username

class PaymentAdmin(admin.ModelAdmin):
  list_display =  ( 'payment_date', 'receipt_nro', 'pay_reference', 'amount', 'apoderado' )
  list_display_links = ( 'apoderado', )
  list_filter = ( 'payment_settings__matricula__seccion', )
  def apoderado(self, obj):
    return obj.payment_settings.matricula.student.apoderado.username

#  def get_form(self, request, obj=None, **kwargs):
#    form = super(PaymentAdmin, self).get_form(request, obj, **kwargs)
#    form.base_fields['amount'].initial = obj.payment_settings.monthly_amount
#    return form

admin.site.register(PaymentSettings, PaymentSettingsAdmin)
admin.site.register(Payment, PaymentAdmin)
