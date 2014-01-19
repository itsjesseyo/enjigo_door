from django.conf.urls.defaults import *
from django.contrib import admin
admin.autodiscover()

import views

urlpatterns = patterns('',
        url(r'^$', views.config_index, name='index'),
    )

# vim: et sw=4 sts=4