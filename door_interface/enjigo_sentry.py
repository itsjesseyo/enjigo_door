import datetime, time
from helpers import Config, Sensor, Cloud, Door, Speaker, Led, Node

############## BEGIN LED #####################
print 'reading settings'
led = Led('led')
led.show_status_light()

# found tag, send response to door mechanism
def found_tag(sensor):
	speaker.play_found_tag_sound()
	led.show_thinking_light()
	sensor.stop()
	valid_tag = tag_is_currently_valid(sensor.last_tag)
	if valid_tag == False:
		valid_response, valid_tag, new_tags = tags_from_cloud(sensor.last_tag)
		if valid_response:
			update_tag_settings(new_tags)

	#ACTIONS BASED ON RESULTS OF TAG
	if valid_tag == True:
		led.show_positive_light()
		speaker.play_positive_sound()
		door.open_door()
		print 'VALID TAG : ' + str(sensor.last_tag)
	else:
		led.show_negative_light()
		speaker.play_negative_sound()
		time.sleep(8)
		led.show_status_light()
		sensor.start()
		print 'ADDED TAG : ' + str(sensor.last_tag)
	

def update_tag_settings(new_tags):
	now = datetime.datetime.now();
	old_tags = settings.file.items('tags')
	days_valid = settings.file.getint('device_info', 'tag_expires_in')
	expiration_date = datetime.datetime.today() + datetime.timedelta(days=days_valid)
	for tag in old_tags:
		print tag[1]
		if str(tag[1]) != 'never':
			settings.file.remove_option('tags', tag[0])
	for tag in new_tags:
		settings.file.set('tags', tag, expiration_date.strftime("%Y-%m-%d"))
	settings.save()

def tags_from_cloud(tag_id):
	data = cloud.get_active_tags(tag_id)
	print '________RESPONSE________: '
	print data
	print '________END_RESPONSE________'
	return data['response'], data['valid_tag'], data['tags']

def tag_is_currently_valid(tag_id):
	current_tags = settings.file.items('tags')
	tag_valid = False
	for tag in current_tags:
		if str(tag[0]) == tag_id:
			if str(tag[1]) == 'never' or tag_is_not_expired(str(tag[1])):
				tag_valid = True
	return tag_valid

def tag_is_not_expired(tag_date_string):
	today = datetime.datetime.today()
	tag_date = datetime.datetime.strptime(tag_date_string, '%Y-%m-%d')
	if today < tag_date:
		return True
	else:
		return False

def door_opened(door):
	time.sleep(door.time_open)
	door.close_door()
	
def door_closed(door):
	led.show_status_light()
	sensor.start()

#node additions
def request_door_open(node):
	led.show_positive_light()
	speaker.play_positive_sound()
	door.open_door()

def request_refresh_users(node):
	valid_response, valid_tag, new_tags = tags_from_cloud('2fe4fd2qf')
	if valid_response:
		update_tag_settings(new_tags)


############## BEGIN CONFIG #####################
print 'reading settings'
settings = Config()
############## BEGIN SPEAKER #####################
print 'reading settings'
speaker = Speaker(settings)
speaker.play_startup_sound()
############## BEGIN CLOUD #####################
print 'initing cloud'
cloud = Cloud(settings)
############## BEGIN DOOR #####################
print 'initing_door'
door = Door('back_door', settings)
door.DOOR_OPENED += door_opened
door.DOOR_CLOSED += door_closed
############## BEGIN NODE ###################
print 'setting up node'
node = Node(settings)
node.OPEN_DOOR_REQUEST += request_door_open
node.REFRESH_USERS_REQUEST += request_refresh_users
node.start()
############## BEGIN SENSOR ###################
print 'setting up sensor'
sensor = Sensor("outside_sensor")
sensor.FOUND_TAG += found_tag
sensor.start()
