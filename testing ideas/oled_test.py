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



sense = SenseHat()
dpad = sense.stick

oled = OLED()

def update():
	events = dpad.get_events()
	for event in events:
		if event.action=="pressed":
			oled.update_stats(event.direction)
			print(event.direction+": "+event.action)
			if event.direction == "middle":
				return 0
	return 1

# def get_ord(some_string):
# 	returnval = 0
# 	for character in some_string:
# 		returnval += ord(character)
# 	return returnval

# returned_ord_val = get_ord('released')


def detect_8dir():
	events = dpad.get_events()
	filter_events = {}
	for event in events:
		get_ord(event.action)


if __name__ == '__main__':
	print("running as main")
	keep_running = 1
	while(keep_running):
		keep_running = update()
	dpad.close()



# # First define some constants to allow easy resizing of shapes.
# # top = -2
# # top = padding
# # bottom = height - top
# # Move left to right keeping track of the current x position for drawing shapes.
# x = 0






# while True:

#     # Draw a black filled box to clear the image.
#     draw.rectangle((0, 0, width, height), outline=0, fill=0)

#     # Shell scripts for system monitoring from here:
#     # https://unix.stackexchange.com/questions/119126/command-to-display-memory-usage-disk-usage-and-cpu-load
#     cmd = "hostname -I | cut -d' ' -f1"
#     IP = subprocess.check_output(cmd, shell=True).decode("utf-8")
#     cmd = 'cut -f 1 -d " " /proc/loadavg'
#     CPU = subprocess.check_output(cmd, shell=True).decode("utf-8")
#     cmd = "free -m | awk 'NR==2{printf \"Mem: %s/%s MB  %.2f%%\", $3,$2,$3*100/$2 }'"
#     MemUsage = subprocess.check_output(cmd, shell=True).decode("utf-8")
#     cmd = 'df -h | awk \'$NF=="/"{printf "Disk: %d/%d GB  %s", $3,$2,$5}\''
#     Disk = subprocess.check_output(cmd, shell=True).decode("utf-8")

#     # Write four lines of text.

#     draw.text((x, top + 0), "IP: " + IP, font=font, fill=255)
#     draw.text((x, top + 8), "CPU load: " + CPU, font=font, fill=255)
#     draw.text((x, top + 16), MemUsage, font=font, fill=255)
#     draw.text((x, top + 25), Disk, font=font, fill=255)

#     # Display image.
#     disp.image(image)
#     disp.show()
#     time.sleep(0.1)
