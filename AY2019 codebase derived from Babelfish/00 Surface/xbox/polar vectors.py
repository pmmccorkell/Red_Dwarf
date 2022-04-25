#run with sudo privileges
#add user to the root group:
#	sudo usermod -a -G root pi
#
#create permissions file using nano
#	sudo nano /etc/udev/rules.d/55-permissions-uinput.rules
#	enter rules:
#		

import xbox
import math
from time import sleep
joystick = xbox.Joystick()

def scalar(a,b):
	# rescale_factor = 1.414213562373095
	returnval = math.sqrt(a**2+b**2)
	return returnval

def angle(a,b):
	degree_conversion = 360 / (2*math.pi)
	# right_angle = math.pi / 2
	#print(degree_conversion)
	if (a==0):
		a=0.000001
	returnval = math.atan(b/a)
	if (a < 0):
		returnval += math.pi
	elif (b < 0):
		returnval += 2*math.pi
	return returnval * degree_conversion

while(1):
	#raw values [-32767,32767]
	# raw_x1 = joystick.leftX()
	# raw_y1 = joystick.leftY()
	# raw_x2 = joystick.rightX()
	# raw_y2 = joystick.rightY()
	# print("raw left :" + str(raw_x1) +", " + str(raw_y1))
	# print("raw right :" + str(raw_x2) +", " + str(raw_y2))

	#tuple scaled and normalized [-1.0,1.0]
	(x1,y1) = joystick.leftStick()
	(x2,y2) = joystick.rightStick()

	scalar1 = scalar(x1,y1)
	vector1 = angle(y1,x1)
	scalar2 = scalar(x2,y2)
	vector2 = angle(y2,x2)
	print()
	print()
	print("scaled left :" + str(x1) +", " + str(y1))
	print("polar left: " + str(vector1) + "deg, " + str(scalar1) + " hypotenuse")
	print()
	print("scaled right :" + str(x2) +", " + str(y2))
	print("polar right: " + str(vector2) + "deg, " + str(scalar2) + " hypotenuse")
	print()
	print()

joystick.close()

