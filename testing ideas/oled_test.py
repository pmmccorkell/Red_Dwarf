# Patrick McCorkell
# June 2021
# US Naval Academy
# Robotics and Control TSD
#

import time
import subprocess
from board import SCL, SDA
import busio
from PIL import Image, ImageDraw, ImageFont
from adafruit_ssd1306 import SSD1306_I2C
from sense_hat import SenseHat



class OLED:
	def __init__(self):
		# Instantiate i2c bus.
		i2c = busio.I2C(SCL, SDA)

		# Instantiate ssd1306 class over i2c.
		# Class(Width, Height, bus)
		self.oled = SSD1306_I2C(128, 32, i2c)
		self.clear_oled()
	
		# Instantiate an image the size of the screen
		self.image = Image.new("1", (self.oled.width, self.oled.height))

		# Instantiate an object to draw on the image.
		self.draw = ImageDraw.Draw(self.image)

		# Instantiate default font.
		self.font = ImageFont.load_default()

		# Instantiate Pi SenseHat.
		# self.sense = SenseHat()

		# Instantiate the joystick on Pi SenseHat
		# self.dpad = sense.stick

	def clear_oled(self):
		# Clear and show display.
		self.oled.fill(0)
		self.oled.show()

	def clear_draw(self):
		# Draw a black rectangle from edge to edge.
		self.draw.rectangle((0, 0, self.oled.width, self.oled.height), outline=0, fill=0)

	def get_IP(self):
		return subprocess.check_output("hostname -I | cut -d' ' -f1",shell=True).decode("utf-8")

	def get_CPU(self):
		return subprocess.check_output('cut -f 1 -d " " /proc/loadavg',shell=True).decode("utf-8")

	def update_stats(self,last_joystick):
		top = -2
		padding = 8
		x = 0

		self.clear_draw()
		dataframe = {
			'IP':self.get_IP(),
			'CPU':self.get_CPU(),
			'dpad':last_joystick
		}
		for index,key in enumerate(dataframe):
			textline = key + ": " + dataframe[key]
			self.draw.text((0,top+(index*padding)), textline,font=self.font,fill=255)
		self.oled.image(self.image)
		self.oled.show()



class Joystick:
	def __init__(self):
		self.sense = SenseHat()
		self.dpad = self.sense.stick

		self.released_val = self.get_ord('released')
		self.held_val = self.get_ord('held')
		self.pressed_val = self.get_ord('pressed')

		self.UP, self.DOWN, self.LEFT, self.RIGHT, self.UPLEFT, self.UPRIGHT, self.DOWNLEFT, self.DOWNRIGHT = 0,0,0,0,0,0,0,0

		self.dpad.direct_right = self.detected_right
		self.dpad.direction_left = self.detected_left
		self.dpad.direction_up = self.detected_up
		self.dpad.direction_down = self.detected_down
		
		self.last_event = 'N/A'

	def get_ord(self,some_string):
		returnval = 0
		for character in some_string:
			returnval += ord(character)
		return returnval

	def close(self):
		self.dpad.close()

	def setup_diags():
		dpad.direction_up = detect_up
		dpad.direction_down = detect_down

	def detected_left(self,event):
		check_val = bool(self.get_ord(event.action) - self.released_val)
		self.LEFT = 1 * check_val
		self.last_event = event.direction
		
	def detected_right(self,event):
		check_val = bool(self.get_ord(event.action) - self.released_val)
		self.RIGHT = 1 * check_val
		self.last_event = event.direction

	def detected_up(self,event):
		check_val = bool(self.get_ord(event.action) - self.released_val)
		self.UP = 1 * check_val
		self.UPLEFT = self.UP * self.LEFT
		self.UPRIGHT = self.UP * self.RIGHT
		self.last_event = event.direction
	
	def detected_down(self,event):
		check_val = bool(self.get_ord(event.action) - self.released_val)
		self.DOWN = 1 * check_val
		self.DOWNLEFT = self.DOWN * self.LEFT
		self.DOWNRIGHT = self.DOWN * self.RIGHT
		self.last_event = event.direction

	def detected_middle(self,event)
		check_val = bool(self.get_ord(event.action) - self.released_val)
		self.last_event = event.direction

oled = OLED()
dpad = Joystick()

def update():
	events = dpad.dpad.get_events()
	for event in events:
		if event.action=="pressed":
			oled.update_stats(event.direction)
			print(event.direction+": "+event.action)
			if event.direction == "middle":
				return 0
	return 1


# if __name__ == '__main__':
# 	print("running as main")
# 	keep_running = 1
# 	while(keep_running):
# 		keep_running = update()
# 	dpad.close()

def update_state():
	oled.update_stats(dpad.last_event)
	if dpad.LEFT and dpad.RIGHT and 

if __name__ == '__main__':
	print("running as main")
	keep_running = 1
	while(keep_running):
		keep_running = update()
	dpad.close()
