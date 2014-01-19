#https://github.com/invisibleroads/socketIO-client
from socketIO_client import SocketIO, BaseNamespace
from event import Event

import hashlib


class Namespace(BaseNamespace, threading.Thread):

	server_is_valid = False

	def __init__(self, settings):
		threading.Thread.__init__(self)
		self.address = settings.file.get("cloud", "node_address")
		self.secret_key = settings.file.get("cloud", "secret_key")

		#events
		self.LOST_CONNECTION = Event()
		self.OPEN_DOOR_REQUEST = Event()

	def on_connect(self):
		print '[Connected]'

	def on_begin_validation(self, data):
		print 'beginning validation'
		hash = hashlib.sha256(data['message'] + self.secret_key).hexdigest()
		if(hash == data['hash']):
			self.server_is_valid = True
			self.complete_validation()

	def complete_validation(self):
		print 'completitng validation'
		message = 'hello there'
		hash = hashlib.sha256(message + self.secret_key).hexdigest()
		self.emit('complete_validation', {'message':message, 'hash':hash})

	def on_open_door(self, data):
		if(self.hash_is_valid(data['message'], data['hash'])):
			self.OPEN_DOOR_REQUEST(self)

	def hash_is_valid(message, hash_to_check):
		hash = hashlib.sha256(data['message'] + self.secret_key).hexdigest()
		if(hash == hash_to_check):
			return True
		else:
			return False


socketIO = SocketIO('localhost', 3000, Namespace)
socketIO.wait(seconds=1)