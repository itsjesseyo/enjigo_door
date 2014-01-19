# Create your views here.
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.admin.views.decorators import staff_member_required
from models import App
import forms

@staff_member_required
def config_index(request, template = 'appsettings/index.html', base_template = 'index.html'):
    apps = sorted(vars(settingsinst).keys())
    return render_to_response(template, 
            {'apps':apps, 'base_template':base_template},
            RequestContext(request))