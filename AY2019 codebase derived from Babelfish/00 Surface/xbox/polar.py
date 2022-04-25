#run with sudo privileges
#add user to the root group:
#	sudo usermod -a -G root pi
#
#create permissions file using nano
#	sudo nano /etc/udev/rules.d/55-permissions-uinput.rules
#	enter rules:
#		

import xbox
from math import sqrt, pi, atan
from time import sleep
joystick = xbox.Joystick()
import serial

max_speed = 210
maintain_facing=1

values = {
		'scalar1':999,
		'vector1':999,
		'scalar2':999,
		'vector2':999,
		'vector2_x2':999
	}

ser=serial.Serial(
	port='/dev/ttyACM0',
	baudrate=115200,
	parity=serial.PARITY_NONE,
	stopbits=serial.STOPBITS_ONE,
	bytesize=serial.EIGHTBITS,
	timeout=1
	)


def scalar(a,b):
	# rescale_factor = 1.414213562373095
	returnval = sqrt(a**2+b**2)
	return returnval

def angle(a,b):
	degree_conversion = 360 / (2*pi)
	if (a==0):
		a=0.000001
	returnval = atan(b/a)
	if (a < 0):
		returnval += pi
	elif (b < 0):
		returnval += 2*pi
	return returnval * degree_conversion
	
def relative(x):
	returnval = (round(x*3))+834
	return returnval

def sample():
	global values
	#tuple scaled and normalized [-1.0,1.0]
	(x1,y1) = joystick.leftStick()
	#print(x1,y1)
	(x2,y2) = joystick.rightStick()

	values = {
		'scalar1':scalar(x1,y1),
		'vector1':angle(y1,x1),
		'scalar2':scalar(x2,y2),
		'vector2':angle(y2,x2),
		'vector2_x2':relative(x2)
		}
	#print(values)

def close():
	sleep(0.1)
	stop_thrusters_command()
	joystick.close()

def stop_thrusters_command():
	writeline=('sto:000').encode()
	ser.write(writeline)
	#print("sent: "+writeline.decode())

def speed_command(speed_str):
	target=int(speed_str)
	if (target<10): prefix='vel:00'
	elif (target<100): prefix='vel:0'
	else: prefix='vel:'
	writeline=(prefix+speed_str).encode()
	ser.write(writeline)
	#print("sent: "+writeline.decode())

def heading_command(heading_str):
	target=int(heading_str)
	if (target<10): prefix='hea:00'
	elif (target<100): prefix='hea:0'
	else: prefix='hea:'
	writeline=(prefix+heading_str).encode()
	ser.write(writeline)
	print("sent: "+writeline.decode())

def offset_command(offset_str):
	target=int(offset_str)
	if (target<10): prefix='off:00'
	elif (target<100): prefix='off:0'
	else: prefix='off:'
	writeline=(prefix+offset_str).encode()
	ser.write(writeline)
	#print("sent: "+writeline.decode())

def check_quit():
	returnval = 0
	if (joystick.leftBumper() and joystick.rightBumper()):
		returnval = 1
	return returnval

def check_maintain():
	global maintain_facing
	if joystick.rightTrigger():
		maintain_facing*=-1
	print(maintain_facing)

def main():
	global max_speed, values, maintain_facing
	maximum = max_speed / 1.2
	fail=0
	while(fail<100):
		try:
			sample()
			fail=0
		except:
			fail+=1
			print("try failed: " + str(fail))
			# stop_thrusters_command()
			# sleep(0.5)
		if (check_quit()):
			fail = 9000
		if (fail==0):
			check_maintain()
			#print(values)
			# f = round(values['vector2'])
			f = round(values['vector2_x2'])
			o = round(values['vector1'])
			s = round(max_speed*values['scalar1'])
			#print()
			#print(f)
			#print(o)
			#print(s)
			#print()
			if (maintain_facing==1):
				# if (h==0):
					# h=999
				heading_command(str(f))
			else:
				heading_command(str(999))
			sleep(0.05)
			if (o==0):
				o=999
			offset_command(str(o))
			sleep(0.05)
			if (s==0):
				s=599
			speed_command(str(s+400))
		sleep(0.1)
	close()


main()

