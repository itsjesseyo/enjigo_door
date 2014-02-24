from pyblinkm import BlinkM, Scripts
import time

class Led():

	def __init__(self, name):
		#so we can have many different leds
		self.name = name
		self.led = BlinkM()
		self.led.reset()
		self.led.set_fade_speed(32)
		

	def show_status_light(self):
		self.led.fade_to_hex("0000ff")

	def show_thinking_light(self):
		#self.led.play_script(Scripts.WHITE_FLASH)
		self.led.fade_to_hex("ffffff")

	def show_positive_light(self):
		#self.led.stop_script()
		self.led.fade_to_hex("00ff00")

	def show_negative_light(self):
		#self.led.stop_script()
		self.led.fade_to_hex("ff0000")
