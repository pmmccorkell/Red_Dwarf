# Patrick McCorkell
# June 2021
# US Naval Academy
# Robotics and Control TSD
#

from time import sleep
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
	def __init__(self,display):
		self.disp = display
		self.sense = SenseHat()
		self.dpad = self.sense.stick

		self.values = {
			'up':0,
			'down':0,
			'left':0,
			'right':0,
			# 'upleft':0,
			# 'upright':0,
			# 'downleft':0,
			# 'downright':0,
			'middle':0
		}

		self.dpad.direction_any = self.detected

		self.last_event = 'N/A'

		self.event_queue=[]

		self.silence_xinput()


	# All this just to run "xinput float x" in bash,
	# 	where x is the integer for the IO device id of the Joystick.
	def silence_xinput(self):
		buffer = subprocess.Popen(["xinput"],stdout=subprocess.PIPE)
		buffer2 = subprocess.run(["grep","Raspberry"],stdin=buffer.stdout,stdout=subprocess.PIPE)
		buffer3 = buffer2.stdout.decode()
		io_id = buffer3.find('id=')

		buffer4=''
		i=3
		while ((not buffer4.endswith('\t')) and i<8):
			buffer4 += buffer3[io_id + i]
			i+=1
		try:
			self.input_id = str(int(buffer4))
			subprocess.run(['xinput','float',self.input_id])
			print("Successfully disabled IO input of Joystick.")
		except:
			print('WARNING: Disabling IO input of Joystick failed.')


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

	def detected(self,event):
		print('detected')
		self.values[event.direction] = 1 * (not bool(event.action.find('released')))
		print(event.direction+': '+str(self.values[event.direction]))
		if not (event.action.find('pressed')):
			self.last_event = event.direction
			self.event_queue.append(event.direction)
			self.update_display()
		# elif not (event.action.find('released')):
		# 	self.values[event.direction] = 0


	def update_display(self):
		while(self.event_queue):
			oled.update_stats(self.event_queue.pop(0))

oled = OLED()
dpad = Joystick(oled)

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
	# oled.update_stats(dpad.last_event)
	# if dpad.UPLEFT:
	# 	print("up left")
	# if dpad.UPRIGHT:
	# 	print("up right")
	if (dpad.values['middle']):
		return 0
	return 1

if __name__ == '__main__':
	print("running as main")
	keep_running = 1
	while(keep_running):
		oled.update_stats(dpad.last_event)
		keep_running = update_state()
		# sleep(0.5)
	dpad.close()
