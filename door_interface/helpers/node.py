#https://github.com/invisibleroads/socketIO-client
from socketIO_client import SocketIO, BaseNamespace
from event import Event

import hashlib, threading, random, string



class Node(threading.Thread):

	server_is_valid = False
	socket = None
	socketIO = None

	def __init__(self, settings):
		threading.Thread.__init__(self)
		self.address = settings.file.get("cloud", "node_address")
		self.port = int(settings.file.get("cloud", "node_port"))
		self.secret_key = settings.file.get("cloud", "secret_key")


		#events
		self.LOST_CONNECTION = Event()
		self.OPEN_DOOR_REQUEST = Event()
		self.REFRESH_USERS_REQUEST = Event()

	def socket_connected(self, *args):
		print "i ma conencted"

	def socket_disconnected(self, *args):
		print 'lost connections'

	def info_message(self, message):
		#obj = json.loads(message)
		print message['msg']

	def on_begin_validation(self, transmission):
		message = transmission['message']
		hash = transmission['hash']
		secure_hash = hashlib.sha256(message + self.secret_key).hexdigest()
		if hash == secure_hash:
			print 'hashes match'
			random_text, secure_hash = self.random_hash()
			self.socketIO.emit('complete_validation', {'message':random_text, 'hash':secure_hash})
		else:
			print 'node has mismatch'

	def on_open_door_request(self, transmission):
		message = transmission['message']
		hash = transmission['hash']
		secure_hash = hashlib.sha256(message + self.secret_key).hexdigest()
		if hash == secure_hash:
			print 'requesting open'
			self.OPEN_DOOR_REQUEST(self)
		else:
			print 'node has mismatch'

	def on_refresh_users_request(self, transmission):
		message = transmission['message']
		hash = transmission['hash']
		secure_hash = hashlib.sha256(message + self.secret_key).hexdigest()
		if hash == secure_hash:
			print 'requestin refresh'
			self.REFRESH_USERS_REQUEST(self)
		else:
			print 'node has mismatch'

	def random_hash(self):
		random_text = "".join( [random.choice(string.letters) for i in xrange(32)] )
		secure_hash = hashlib.sha256(random_text + self.secret_key).hexdigest()
		return random_text, secure_hash

	def connect(self):
		print self.address + ":" + str(self.port)
		self.socketIO = SocketIO(self.address, self.port)
		self.socketIO.on('connect', self.socket_connected)
		self.socketIO.on('disconnect', self.socket_disconnected)
		self.socketIO.on('close', self.socket_disconnected)
		self.socketIO.on_disconnect = self.socket_disconnected
		self.socketIO.on('begin_validation', self.on_begin_validation)
		self.socketIO.on('open_door_request', self.on_open_door_request)
		self.socketIO.on('refresh_users_request', self.on_refresh_users_request)
		self.socketIO.wait()



