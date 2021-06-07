# Patrick McCorkell
# April 2021
# US Naval Academy
# Robotics and Control TSD
#

# run with sudo privileges
# add user to the root group:
#	sudo usermod -a -G root pi
#
# create permissions file using nano
#	sudo nano /etc/udev/rules.d/55-permissions-uinput.rules
#	enter rules:
#		

from xbox import Joystick
from math import sqrt, pi, atan
from math import tau as twopi
from time import sleep
# from surface import *
# import atexit

class XBoxController:
	def __init__(self,communicator):
		self.DEBUG = 0
		self.joystick = Joystick()
		self.comms = communicator
		self.max_speed = 500

		self.values = {
			'scalar1':999,
			'vector1':999,
			'scalar2':999,
			'vector2':999,
			'vector2_x2':999,
			'maintain' : 1,
			'mode' : 1
		}

	def scalar(self,a,b):
		# rescale_factor = 1.414213562373095
		returnval = sqrt(a**2+b**2)
		return returnval

	def angle(self,a,b):
		degree_conversion = 360 / twopi
		if (a==0):
			a=0.000001
		returnval = atan(b/a)
		if (a < 0):
			returnval += pi
		elif (b < 0):
			returnval += twopi
		return returnval * degree_conversion

	def relative(self,x):
		returnval = (round(x*3))+834
		return returnval

	def check_quit(self):
		return (self.joystick.leftBumper() and self.joystick.rightBumper())

	def sample(self):
		# self.values
		#tuple scaled and normalized [-1.0,1.0]
		(x1,y1) = self.joystick.leftStick()
		#print(x1,y1)
		(x2,y2) = self.joystick.rightStick()

		new_values = {
			'scalar1':self.scalar(x1,y1),
			'vector1':self.angle(y1,x1),
			'scalar2':self.scalar(x2,y2),
			'vector2':self.angle(y2,x2),
			'vector2_x2':self.relative(x2),
			'maintain' : self.values['maintain'] ^ self.joystick.rightBumper(),
			'mode' : self.values['mode'] ^ self.joystick.leftBumper(),
			'quit' : self.check_quit()
		}
		self.values = new_values
		if (self.DEBUG):
			print(self.values)
		return new_values

	def process(self):
		samples = self.sample()

		self.return_dict = {
			'facing' : round(samples['vector2_x2']),
			'offset' : round(samples['vector1']),
			'speed' : round(self.max_speed*samples['scalar1']),		# if speed is < 10, set to 0
			'maintain' : samples['maintain'],
			'mode' : samples['mode'],
			'quit' : samples['quit']
		}
		if (self.DEBUG):
			print()
			for k,v in self.return_dict:
				print(str(k)+": "+str(v))
			print()
		self.comms.send(self.return_dict)
		# return return_dict

	def stream(self):
		while(1):
			self.process()
			sleep(0.008)

	def close(self):
		sleep(0.1)
		print("turning off xbox controller")
		self.joystick.close()
