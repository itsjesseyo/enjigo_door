from django.conf.urls import patterns, url
from django.contrib import admin
from django.db.models import get_apps, get_models, signals
from django.forms import ModelForm
from django.forms.formsets import formset_factory
from django import forms as django_forms
from models import Setting, Group
from django.core.context_processors import csrf
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.contrib.admin.validation import validate
from django.shortcuts import render_to_response
from django.template.defaultfilters import capfirst
from background import config as bg_config
from django.utils.safestring import mark_safe



class SettingForm(ModelForm):

	class Meta:
		model = Setting
		#fields = ('value','key','read_only','help_text')
		exclude = ('group','key','read_only','help_text')



class SettingAdmin(admin.ModelAdmin):


	#list_display = ['value']
	#list_editable = ['value',]
	#list_filter = ['group']
	#list_display_links = ('key',)


	def get_form(self, request, obj=None, **kwargs):
	
		return super(SettingAdmin, self).get_form(request, obj, **kwargs)

	def has_add_permission(self, request):
		return False

	def my_view(self, request):
		# custom view which should return an HttpResponse
		pass

	def get_urls(self):
		urls = super(SettingAdmin, self).get_urls()
		my_urls = patterns(' ', (r'^$', self.admin_site.admin_view(self.changelist_view)), )        

		return my_urls + urls

	#override Django's changelist_view to render out my own change list as single grouped settings page
	def changelist_view(self, request, extra_context=None):
		from django.contrib.admin.views.main import ChangeList, ERROR_FLAG
		#get database_settings
		default_settings = get_all_default_settings()
		# retrieve database repsentations for forms
		database_settings = get_or_create_database_settings(default_settings)
		settings_forms = {}
		if request.method == "POST":
			for group, db_settings in database_settings.iteritems():
				forms = list()
				for x in range(len(db_settings)):
					form = SettingForm(request.POST, prefix=group + "-" + str(x), instance=db_settings[x])
					if form.is_valid():
						form.save()
					form.fields['value'].help_text = db_settings[x].help_text
					form.fields['value'].label = db_settings[x].key.replace('_', ' ') + ' '
					forms.append(form)
				settings_forms[group] = forms
		else:
			for group, db_settings in database_settings.iteritems():
				forms = list()
				for x in range(len(db_settings)):
					form = SettingForm(prefix=group + "-" + str(x), instance=db_settings[x], )
					form.fields['value'].help_text = db_settings[x].help_text
					form.fields['value'].label = db_settings[x].key.replace('_', ' ') + ' '
					#form.value.help_text = db_settings[x].help_text
					forms.append(form)
				#forms = [SettingForm(prefix=group + "-" + str(x), instance=db_settings[x]) for x in range(len(db_settings))]
				settings_forms[group] = forms
				#settings_forms[group] = len(forms)
		context = {
			'settings_forms':settings_forms,
			#'default_settings':len(database_settings)
			'app_list':self.app_list(request),
			'default_settings':settings.CONFIG_DEFAULT_SETTINGS
		}
		extra_context = extra_context or {}
		context.update(extra_context)
		context.update(csrf(request))
		return render_to_response('config/changelist.html', context)

	def app_list(self, request):
		'''
		Get all models and add them to the context apps variable.
		'''
		user = request.user
		app_dict = {}
		admin_class = SettingAdmin
		for model in get_models():
			validate(admin_class, model)
			model_admin = admin_class(model, None)
			app_label = model._meta.app_label
			#if app_label in IGNORE_MODELS:
				#continue
			has_module_perms = user.has_module_perms(app_label)
			if has_module_perms:
				perms = model_admin.get_model_perms(request)
				# Check whether user has any perm for this module.
				# If so, add the module to the model_list.
				if True in perms.values():
					model_dict = {
						'name': capfirst(model._meta.verbose_name_plural),
						'admin_url': mark_safe('%s/%s/' % (app_label, model.__name__.lower())),
					}
					if app_label in app_dict:
						app_dict[app_label]['models'].append(model_dict)
					else:
						app_dict[app_label] = {
							'name': app_label.title(),
							'app_url': app_label + '/',
							'has_module_perms': has_module_perms,
							'models': [model_dict],
						}
		app_list = app_dict.values()
		app_list.sort(key=lambda x: x['name'])
		for app in app_list:
			app['models'].sort(key=lambda x: x['name'])
		return {'apps': app_list}

#gets at default settings form all apps with config.py
def get_all_default_settings():
	existing_settings = settings.CONFIG_DEFAULT_SETTINGS
	new_settings = bg_config.default_settings
	merged_settings = merge_default_settings(existing_settings, new_settings)
	#find other settings and merge
	#override newer settings as found
	return	merged_settings

#called repeatedly by get_all_default_settings.used to merge defaults into single dicitonary
def merge_default_settings(existing_settings, new_settings):
	if len(new_settings) > 0:
		for group, settings in new_settings.iteritems():
			if not group in existing_settings:
				existing_settings[group] = settings
			else:
				for key, value in settings.iteritems():
					existing_settings[group][key] = value #database setting wins
	return existing_settings

#if default doesnt exist, create one and add it to array
def get_or_create_database_settings(default_settings):

	grouped_settings = {}

	for group, settings in default_settings.iteritems():
		try:
			db_group = Group.objects.get(name=group)
		except:
			db_group = Group(name=group)
			db_group.save()

		for key, values in settings.iteritems():
			try:
				db_setting = db_group.setting_set.get(key=key)
			except:
				db_setting = db_group.setting_set.create(key=key, value=values[0], help_text=values[1], read_only=values[2])
				db_setting.save()

		grouped_settings[group] = db_group.setting_set.all()
	return grouped_settings


admin.site.register(Setting, SettingAdmin)







