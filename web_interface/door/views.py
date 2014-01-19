# Create your views here.
from django.http import HttpResponse
from django.utils import simplejson
from django.core import serializers
from django.shortcuts import render
from datetime import datetime 
from django.http import HttpResponse
from django.utils import simplejson
from django.http import Http404
from django.conf import settings
from door.models import Tag, Activity
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required


import hashlib

################## check rfid tags ######################
class valid_hash:

	def __init__(self, f):
		self._f = f

	def __call__(self, *args, **kwargs):
		secure_hash = hashlib.sha256(kwargs["udid"] + settings.SECRET_KEY).hexdigest()
		if secure_hash == kwargs["hash"]:
			return self._f(*args, **kwargs)
		else:
			#raise Http404
			data = {'response':False}
			return HttpResponse(simplejson.dumps(data), mimetype='application/json')

@valid_hash
def get_active_keys(*args, **kwargs):
	tag = Tag.objects.filter(key=kwargs['tag_id'], active=True)
	valid_tag = False
	if len(tag) > 0:
		valid_tag=True
		tag = tag[0]
		tag.last_entry = datetime.now()
		tag.save()
		create_activity(tag)
	else:
		create_inactive_tag(kwargs['tag_id'])#auto adds unkown keys ot list
	tags = Tag.objects.filter(active=True)
	tag_list = []
	for tag in tags:
		tag_list.append(str(tag.key))
	context = {
		'response':True,
		'valid_tag':valid_tag,
		'tags':tag_list
	}
	
	return HttpResponse(simplejson.dumps(context), mimetype='application/json')

def create_inactive_tag(tag_id):
	tag = Tag.objects.filter(key=tag_id)
	tag_exists = False
	if len(tag) > 0:
		create_activity(tag)
	else:
		tag = Tag(key=tag_id, active=False, user='unkown')
		tag.save()

def create_activity(tag):
	activity = Activity(tag=tag)
	activity.save()

@login_required
def show_admin(request):
	#get most recent inactive keys
	inactive_tags = Tag.objects.filter(active=False).order_by('-created')
	active_tags = Tag.objects.filter(active=True).order_by('-created')
	#get other keys
	#get door status
	return render(request, 'door/index.html', {
        'inactive_tags': inactive_tags,
        'active_tags': active_tags,
    })


	
######################## unlock by command ########################
class valid_user:

	def __init__(self, f):
		self._f = f

	def __call__(self, *args, **kwargs):
		username = kwargs["username"]
		seed_value = kwargs["seed_value"]
		hashed_password = kwargs["hash"]
		# need to get users password
		password = ''

		secure_hash = hashlib.sha256(username + settings.SECRET_KEY + seed_value + password).hexdigest()
		if secure_hash == hashed_password:
			return self._f(*args, **kwargs)
		else:
			#raise Http404
			data = {'response':False}
			return HttpResponse(simplejson.dumps(data), mimetype='application/json')

@valid_user
def open_says_me(*args, **kwargs):
	pass
