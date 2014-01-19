from django.conf.urls import patterns, url
from door.views import get_active_keys, open_says_me, show_admin

urlpatterns = patterns('',
    url('^retrieve/active_tags/(?P<udid>.*)/(?P<hash>.*)/(?P<tag_id>.*)', get_active_keys, name='active_keys'),
    url('^door_command/unlock/(?P<user_name>.*)/(?P<hash>.*)/(?P<seed_value>.*)', open_says_me, name='open_says_me'),
    url('^admin', show_admin, name='admin'),
    url('^login/$', 'django.contrib.auth.views.login', {'template_name':'door/login.html', 'redirect_field_name': '/door/admin/'}),

)