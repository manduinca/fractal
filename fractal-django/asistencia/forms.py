# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import ApoderadoUser

class ApoderadoUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm):
        model = ApoderadoUser
        fields = UserCreationForm.Meta.fields + ('dni',)

class ApoderadoUserChangeForm(UserChangeForm):
    class Meta:
        model = ApoderadoUser
        fields = UserCreationForm.Meta.fields + ('dni',)
