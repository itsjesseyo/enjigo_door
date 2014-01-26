from django.conf.urls import patterns, url
from door.views import get_active_keys, open_says_me, show_admin, update_tag, remote_refresh

urlpatterns = patterns('',
    url('^admin/remote/refresh', remote_refresh, name='remote_refresh'),


	url('^retrieve/active_tags/(?P<udid>.*)/(?P<hash>.*)/(?P<tag_id>.*)', get_active_keys, name='active_keys'),
	url('^admin/tag/update/(?P<tag_id>.*)/(?P<name>.*)/(?P<active>.*)', update_tag, name='update_tag'),
	url('^admin/remote/open', open_says_me, name='open_says_me'),
	url('^login/$', 'django.contrib.auth.views.login', {'template_name':'door/login.html', 'redirect_field_name': '/door/admin/'}),
	url('^admin', show_admin, name='admin'),

)

