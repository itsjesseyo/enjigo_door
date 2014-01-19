import sys, serial, time
import MFRC522
import RPi.GPIO as GPIO
from event import Event

class Door():

	def __init__(self, name, settings):
		#so we can have many different doors
		self.name = name
		self.pin = settings.file.getint('door', 'pin')
		#in seconds
		self.time_open = settings.file.getint('door', 'time_open')
		GPIO.setmode(GPIO.BOARD)
		#GPIO.setwarnings(False)
		# GPIO.setup(channel, GPIO.OUT, initial=GPIO.HIGH)
		GPIO.setup(self.pin, GPIO.OUT)
		# need to make sure door is locked on init
		GPIO.output(self.pin, False)

		#EVENTS
		self.DOOR_OPENED = Event()
		self.DOOR_CLOSED = Event()

	def open_door(self):
		#if relay is configured as normally open, 
		#setting pin to LOW closes the connection and opens the door
		GPIO.output(self.pin, True)
		self.DOOR_OPENED(self)

	def close_door(self):
		GPIO.output(self.pin, False)
		self.DOOR_CLOSED(self)