from socketIO_client import SocketIO, BaseNamespace
import threading
import hashlib



import ConfigParser, uuid, os

class Config:

	def __init__(self):
		self.check_file()
		self.file = self.retrieve()

	def check_file(self):
		fd = os.open('settings.cfg', os.O_CREAT)
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



# copy of helpers event for ease of testing
class Event:
	def __init__(self):
		self.handlers = set()

	def handle(self, handler):
		self.handlers.add(handler)
		return self

	def unhandle(self, handler):
		try:
			self.handlers.remove(handler)
		except:
			raise ValueError("Handler is not handling this event, so cannot unhandle it.")
		return self

	def fire(self, *args, **kargs):
		for handler in self.handlers:
			handler(*args, **kargs)

	def getHandlerCount(self):
		return len(self.handlers)

	__iadd__ = handle
	__isub__ = unhandle
	__call__ = fire
	__len__  = getHandlerCount



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
			self.socketIO.emit('complete_validation', {'message':message, 'hash':hash})
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

	def connect(self):
		print self.address + ":" + str(self.port)
		self.socketIO = SocketIO(self.address, self.port)
		self.socketIO.on('connect', self.socket_connected)
		self.socketIO.on('disconnect', self.socket_disconnected)
		self.socketIO.on('close', self.socket_disconnected)
		self.socketIO.on_disconnect = self.socket_disconnected
		self.socketIO.on('error', self.socket_disconnected)
		self.socketIO.on('begin_validation', self.on_begin_validation)
		self.socketIO.on('open_door_request', self.on_open_door_request)
		self.socketIO.on('refresh_users_request', self.on_refresh_users_request)
		self.socketIO.wait()







############## BEGIN CONFIG #####################
print 'reading settings'
settings = Config()
############## node #####################
node = Node(settings)
node.connect()






