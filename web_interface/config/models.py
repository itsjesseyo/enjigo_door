from django.db import models
#import logging
# Create your models here.

class Group(models.Model):
	name = models.CharField(max_length=64)

	def __unicode__(self):
		return self.name



class Setting(models.Model):
	group = models.ForeignKey(Group)
	key = models.CharField(max_length=64, verbose_name='setting')
	value = models.CharField(max_length=64)
	help_text = models.CharField(max_length=256)
	read_only = models.BooleanField(default=False)
	
	def __unicode__(self):
		return self.key




class ConfigFor():

	def __init__(self, desired_group):
		group = Group.objects.filter(name=desired_group)
		#logging.info("group : " + str(len(group)) + "\n\n")
		if len(group) > 0:
			group = group[0]
			group_settings = group.setting_set.all()
			self.settings = {}
			for setting in group_settings:
				self.settings[setting.key] = setting.value
		else:
			self.settings = {}