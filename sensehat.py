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
from pwmControl import pwmControl



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
		self.silence_xinput()
		self.disp = display
		self.sense = SenseHat()
		self.dpad = self.sense.stick

		self.values = {
			'up':0,
			'down':0,
			'left':0,
			'right':0,
			'middle':0
		}

		self.thrusters = pwmControl()
		self.thruster_test_val = 40
		self.map_functions = {
			'right':self.thrusters.forePort,
			'down':self.thrusters.foreStar,
			'left':self.thrusters.aftStar,
			'up':self.thrusters.aftPort,
			'default':self.thrusters.stopAllThrusters
		}


		self.dpad.direction_any = self.detected

		self.last_event = 'N/A'

		self.event_queue=[]


	# All this just to run "xinput float x" in bash,
	# 	where x is the integer for the Device ID of the Joystick in xinput.
	#	xinput is the plug-and-play I/O handler for various Ubuntu-like distros.
	def silence_xinput(self):
		# Run xinput in bash, and save the result in the buffer.
		buffer = subprocess.Popen(["xinput"],stdout=subprocess.PIPE)

		# Feed the result of buffer as an argument to bash, run grep searching for "Raspberry" (joystick), and save result to buffer2
		buffer2 = subprocess.run(["grep","Raspberry"],stdin=buffer.stdout,stdout=subprocess.PIPE)

		# char array -> str
		buffer = buffer2.stdout.decode()

		# Find the ID value in buffer.
		io_id = buffer.find('id=')

		# In case the ID is 2 digits or more, iterate over a few digits until a 'tab' is found.
		buffer2=''
		i=3
		while ((not buffer2.endswith('\t')) and i<8):
			buffer2 += buffer[io_id + i]
			i+=1

		# If the ID is not properly found, may fail on the str(int(...)).
		# If the ID is invalid, may fail on the subprocess.run(...)
		# input_id is saved as a Class Property (self.___) to facilitate debugging.
		try:
			self.input_id = str(int(buffer2))
			subprocess.run(['xinput','float',self.input_id])
			print("Successfully disabled IO input of Joystick.")
		except:
			print("WARNING: Disabling IO input of Joystick failed.")


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

	def run_thruster(self):
		thrusters_function = self.map_functions.get(self.last_event, self.map_functions['default'])
		thrusters_function(self.thruster_test_val)
	
	def stop_thrusters(self):
		self.thrusters.stopAllThrusters()

	def detected(self,event):
		print('detected')
		self.values[event.direction] = 1 * (not bool(event.action.find('released')))
		print(event.direction+': '+str(self.values[event.direction]))
		translate = {
			'right':'fore Port',
			'down':'fore Star',
			'left':'aft Star',
			'up':'aft Port',
			'default':'N/A'
		}
		if not (event.action.find('pressed')):
			self.last_event = event.direction

			# self.event_queue.append(event.direction)
			js_position = translate.get(event.direction,translate['default'])
			print(js_position)
			self.event_queue.append(js_position)
			self.update_display()
			self.run_thruster()
		elif not (event.action.find('released')):
			self.stop_thrusters()

	def update_display(self):
		while(self.event_queue):
			self.disp.update_stats(self.event_queue.pop(0))

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


def update_state():
	if (dpad.values['middle']):
		return 0
	return 1


def exit_program():
	import pwmControl
	thrust = pwmControl.pwmControl()
	for i in range(4):
		print("exiting program")
		thrust.stopAllThrusters()
		sleep(i)

if __name__ == '__main__':
	import atexit
	atexit.register(exit_program)

	print("running as main")
	keep_running = 1
	while(keep_running):
		# oled.update_stats(dpad.last_event)
		keep_running = update_state()
		# thrusters_function = map_functions.get(dpad.last_event, map_functions['default'])
		# thrusters_function(40)
		# sleep(0.5)
	dpad.thrusters.exitProgram()
	dpad.close()
	# thrusters.exitProgram()
