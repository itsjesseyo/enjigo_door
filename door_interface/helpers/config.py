import ConfigParser, uuid, os

class Config:

	def __init__(self):
		self.check_file()
		self.file = self.retrieve()

	def check_file(self):
		fd = os.open('/home/pi/enjigo_door/door_interface/settings.cfg', os.O_CREAT)
		os.close(fd)

	def update_setting(self, new_setting):
		config = ConfigParser.ConfigParser()
		config.optionxform = str
		fp = open('settings.cfg')
		config.readfp(fp)
		config.set(new_setting["section"], new_setting["option"], new_setting["value"])
		with open('settings.cfg', 'wb') as configfile:
			config.write(configfile)
			fp.close()

	def save(self):
		with open('settings.cfg', 'wb') as configfile:
			self.file.write(configfile)


	# does everything to get the settings for you
	def retrieve(self):

		config = ConfigParser.ConfigParser()
		config.optionxform = str
		fp = open('settings.cfg')
		config.readfp(fp)


		if config.getboolean('first_run', 'is_first'):
			self.update_setting({'section':'device_info', 'option':'door_id', 'value':str(uuid.uuid1())})
			self.update_setting({'section':'first_run', 'option':'is_first', 'value':False})
			config.set('device_info', 'door_id', str(uuid.uuid1()))
			
			config = ConfigParser.ConfigParser()
			config.optionxform = str
			fp = open('settings.cfg')
			config.readfp(fp)

		return config

