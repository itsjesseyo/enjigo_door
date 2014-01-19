from django.contrib import admin
from door.models import Tag

class TagAdmin(admin.ModelAdmin):
	list_display = ['user', 'key' , 'active', 'created', 'last_entry']
	list_editable = ['active',]
	ordering = ('-created',)




admin.site.register(Tag, TagAdmin)