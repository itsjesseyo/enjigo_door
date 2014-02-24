from pyblinkm import BlinkM, Scripts
import datetime, time

class Led():

	def __init__(self, name):
		#so we can have many different leds
		self.name = name
		self.led = BlinkM()
		self.delay(2)
		self.led.reset()
		self.delay(1)
		self.led.set_fade_speed(32)
		self.delay(1)
	
	def delay(self, seconds):
		time.sleep(seconds)

	def show_status_light(self):
		self.led.fade_to_hex("0000ff")
		self.delay(1)

	def show_thinking_light(self):
		#self.led.play_script(Scripts.WHITE_FLASH)
		self.led.fade_to_hex("ffffff")
		self.delay(1)

	def show_positive_light(self):
		#self.led.stop_script()
		self.led.fade_to_hex("00ff00")
		self.delay(1)

	def show_negative_light(self):
		#self.led.stop_script()
		self.led.fade_to_hex("ff0000")
		self.delay(1)
