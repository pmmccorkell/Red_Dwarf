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

joystick = Joystick()

values = {
	'scalar1':999,
	'vector1':999,
	'scalar2':999,
	'vector2':999,
	'vector2_x2':999,
	'maintain' : 1,
	'mode' : 1
}

def scalar(a,b):
	# rescale_factor = 1.414213562373095
	returnval = sqrt(a**2+b**2)
	return returnval

def angle(a,b):
	degree_conversion = 360 / twopi
	if (a==0):
		a=0.000001
	returnval = atan(b/a)
	if (a < 0):
		returnval += pi
	elif (b < 0):
		returnval += twopi
	return returnval * degree_conversion

def relative(x):
	returnval = (round(x*3))+834
	return returnval

def check_quit():
	return (joystick.leftBumper() and joystick.rightBumper())

def sample():
	global values
	#tuple scaled and normalized [-1.0,1.0]
	(x1,y1) = joystick.leftStick()
	#print(x1,y1)
	(x2,y2) = joystick.rightStick()

	new_values = {
		'scalar1':scalar(x1,y1),
		'vector1':angle(y1,x1),
		'scalar2':scalar(x2,y2),
		'vector2':angle(y2,x2),
		'vector2_x2':relative(x2),
		'maintain' : values['maintain'] ^ joystick.rightBumper(),
		'mode' : values['mode'] ^ joystick.leftBumper(),
		'quit' : check_quit()
	}
	values = new_values
	if (DEBUG):
		print(values)
	return new_values

def process():
	samples = sample()

	return_dict = {
		'facing' : round(samples['vector2_x2']),
		'offset' : round(samples['vector1']),
		'speed' : max(round(max_speed*samples['scalar1']) - 10, 0),		# if speed is < 10, set to 0
		'maintain' : samples['maintain'],
		'mode' : samples['mode'],
		'quit' : samples['quit']
	}
	if (DEBUG):
		print()
		for k,v in return_dict:
			print(str(k)+": "+str(v))
		print()
	return return_dict

def close():
	sleep(0.1)
	stop_thrusters_command()
	print("turning off xbox controller")
	joystick.close()
