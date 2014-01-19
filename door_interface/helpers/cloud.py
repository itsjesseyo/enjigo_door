import json, urllib2, time, threading, hashlib, requests
from event import Event

class Cloud(threading.Thread):
	def __init__(self, settings):
		threading.Thread.__init__(self)
		self.address = settings.file.get("cloud", "address")
		self.door_id = settings.file.get("device_info", "door_id")
		self.secret_key = settings.file.get("cloud", "secret_key")
		# self.authorize_interval = settings.file.getfloat("cloud", "authorize_interval") #how often to check to authroize and get secret key
		# self.sync_interval = settings.file.getfloat("cloud", "sync_interval") #how often to update settings from server

		#EVENTS
		# self.UPDATE_SETTING = Event()
		# self.REQUESTING_STATUS = Event()

	def test(self):
		pass

	def hash(self):
		return hashlib.sha256( str(self.door_id) + str(self.secret_key) ).hexdigest()

	def list_to_address(self, words):
		address = ""
		for word in words[:-1]:
			address+=word+"/"
		address+=words[-1]
		return address

	def get_active_tags(self, tag_id):
		# create hash from secret_key and door_id
		request = self.list_to_address([self.address, "retrieve/active_tags", self.door_id, self.hash(), tag_id])
		print 'WEB_ADDRESS : %s' % request
		try:		
			result = requests.get(request)
			result.raise_for_status()
			print 'RESULT : %s' % result
			response = result.json()#should check to see if response was valid first
		except requests.exceptions.RequestException as e:
			print 'CLOUD_FAIL : %s' % e
			response = {
				'response':False,
				'valid_tag':False,
				'tags':False
			}

		return response
