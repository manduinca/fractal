# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.template import loader


def home_view(request):
    template = loader.get_template('index.html')
    return HttpResponse(template.render({}, request))

