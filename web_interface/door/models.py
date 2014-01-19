from django.db import models
from django.utils.safestring import mark_safe
from s3direct.fields import S3DirectField

# Create your models here.
class Tag(models.Model):
	key = models.CharField(max_length=256)
	user = models.CharField(max_length=256)
	active = models.BooleanField(default=True)
	created = models.DateTimeField(auto_now_add=True)
	last_entry = models.DateTimeField(null=True, editable=False)

	admin_order_field = 'created'

	def __unicode__(self):
		return self.user

	# class Meta:
	# 	ordering = ['created']

# Create your models here.
class Activity(models.Model):
	tag = models.ForeignKey(Tag)
	created = models.DateTimeField(auto_now_add=True)


	def __unicode__(self):
		return self.created