# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from .forms import ApoderadoUserCreationForm, ApoderadoUserChangeForm
from .models import ApoderadoUser, Teacher, Grado, Seccion, Subject, Student, Matricula, Asistencia, Grade, Schedule, YearSettings, Tutor, Incident
# Register your models here.

class AsistenciaAdmin(admin.ModelAdmin):
    search_fields = [ 'student', ]
    list_display = ( 'student', 'hour' )

class StudentAdmin(admin.ModelAdmin):
    search_fields = [ 'first_name', 'last_name', ]
    list_display = ( 'first_name', 'last_name', 'apoderado' )

class TeacherAdmin(admin.ModelAdmin):
    list_display = ( 'first_name', 'last_name', )

class TutorAdmin(admin.ModelAdmin):
    list_display = ( 'teacher', 'seccion', 'year', )
#class ScheduleAdmin(admin.ModelAdmin):
#    list_display = ('grade', 'section', 'schedule')

class GradoAdmin(admin.ModelAdmin):
    list_display = ('name','entrada')

class MatriculaAdmin(admin.ModelAdmin):
    #search_fields = [ 'seccion', ]
    list_display = ( 'yearsettings', 'student', 'seccion', 'get_apoderado' )
    list_display_links = ( 'student', 'get_apoderado', )
    list_filter = ( 'seccion', )
    def get_apoderado(self, obj):
        return obj.student.apoderado

class YearSettingsAdmin(admin.ModelAdmin):
    list_display = ( 'year', 'start_date', 'end_date', 'holidays')

class GradeAdmin(admin.ModelAdmin):
    list_display = ( 'student', 'subject', 'grade_type', 'grade', 'date' )

class SubjectAdmin(admin.ModelAdmin):
    list_display = ( 'name', 'seccion', 'schedule' )
    list_filter = ( 'seccion', )

class SeccionAdmin(admin.ModelAdmin):
    list_display = ( 'section', 'grado', 'name' )

class ApoderadoDataInline(admin.StackedInline):
    model = ApoderadoUser
    can_delete = False
    max_num = 1
    verbose_name_plural = 'Datos Personales'
    #fields = ( 'dni', 'first_name', 'last_name', 'email', 'groups',)
    fieldsets = (
        (None, {
            'fields': ('dni', 'first_name', 'last_name', 'email', 'groups')
        }),
    )
    #fk_name = 'user'

class ApoderadoUserAdmin(UserAdmin):
    pass
    list_display = ( 'username', 'first_name', 'last_name', 'dni' )
    #inlines = (ApoderadoDataInline,)
    add_form = ApoderadoUserCreationForm
    form = ApoderadoUserChangeForm
    model = ApoderadoUser
    
    #fieldsets = (
    #    (None, {
    #        'fields': ('dni', 'first_name', 'last_name', 'email', 'groups')
    #    }),
    #)
    #def add_view(self, *args, **kwargs):
    #    self.inline_instances = []
    #    return super(ApoderadoUserAdmin, self).add_view(*args, **kwargs)

    #def change_view(self, *args, **kwargs):
    #    self.inline_instances.append(ApoderadoDataInline(self.model, self.admin_site))
    #    return super(ApoderadoUserAdmin, self).change_view(*args, **kwargs)
    #def get_inline_instances(self, request, obj=None):
    #    if not obj:
    #        return list()
    #    return super(ApoderadoUserAdmin, self).get_inline_instances(request, obj)
    #fieldsets += ('dni',)
    #model = ApoderadoUser

class ApoderadoUserAdmin2(admin.ModelAdmin):
    list_display = ( 'username', 'first_name', 'last_name', 'dni' )
    search_fields = [ 'username', ]

class IncidentAdmin(admin.ModelAdmin):
    list_display = ( 'points', 'date', 'incident', 'student' )
    search_fields = [ 'student', ]

admin.site.register(ApoderadoUser, ApoderadoUserAdmin2)
#admin.site.register(ApoderadoUser)
admin.site.register(Teacher, TeacherAdmin)
admin.site.register(Grado, GradoAdmin)
admin.site.register(Seccion, SeccionAdmin)
admin.site.register(Subject, SubjectAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Matricula, MatriculaAdmin)
admin.site.register(Tutor, TutorAdmin)
admin.site.register(Asistencia, AsistenciaAdmin)
admin.site.register(Grade, GradeAdmin)
#admin.site.register(Schedule, ScheduleAdmin)
admin.site.register(YearSettings, YearSettingsAdmin)
admin.site.register(Incident, IncidentAdmin)
