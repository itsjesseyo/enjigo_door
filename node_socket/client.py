# from ws4py.client.threadedclient import WebSocketClient

# class DummyClient(WebSocketClient):
#     def opened(self):
#         def data_provider():
#             for i in range(1, 200, 25):
#                 yield "#" * i

#         self.send(data_provider())

#         for i in range(0, 200, 25):
#             print i
#             self.send("*" * i)

#     def closed(self, code, reason=None):
#         print "Closed down", code, reason

#     def received_message(self, m):
#         print m
#         if len(m) == 175:
#             self.close(reason='Bye bye')

# if __name__ == '__main__':
#     try:
#         ws = DummyClient('ws://localhost:3000/', protocols=['http-only', 'chat'])
#         ws.connect()
#         ws.run_forever()
#     except KeyboardInterrupt:
#         ws.close()

# from websocket import create_connection
# ws = create_connection("http://localhost:3000")
# print "Sending 'Hello, World'..."
# ws.send("Hello, World")
# print "Sent"
# print "Reeiving..."
# result =  ws.recv()
# print "Received '%s'" % result
# ws.close()

# from socketIO_client import SocketIO

# def on_connection(*args):
#     print 'entrance : ', args

# socketIO = SocketIO('localhost', 3000)
# socketIO.on('aaa_response', on_connection)
# socketIO.emit('aaa')
# socketIO.wait(seconds=1)


from socketIO_client import SocketIO, BaseNamespace
import hashlib


class Namespace(BaseNamespace):

	door_key = 'dsfgdfasdd'
	admin_key = 'j675h46f354'
	server_is_valid = False

	def on_connect(self):
		print '[Connected]'

	def on_entrance(self, data):
		self.emit('share', {'message':'i am sharing'})
		print 'entrace : ', data['message']

	def on_share(self, data):
		print 'share echo : ', data['message']

	def on_begin_validation(self, data):
		print 'beginning validation'
		hash = hashlib.sha256(data['message'] + self.door_key).hexdigest()
		if(hash == data['hash']):
			self.server_is_valid = True
			self.complete_validation()

	def complete_validation(self):
		print 'completitng validation'
		message = 'hello there'
		hash = hashlib.sha256(message + self.admin_key).hexdigest()
		self.emit('complete_validation', {'message':message, 'hash':hash})

socketIO = SocketIO('localhost', 3000, Namespace)
socketIO.wait(seconds=1)