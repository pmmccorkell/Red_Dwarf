# run with sudo privileges
# add user to the root group:
#	sudo usermod -a -G root pi
#
# create permissions file using nano
#	sudo nano /etc/udev/rules.d/55-permissions-uinput.rules
#	enter rules:
#		

import xbox
from math import sqrt, pi, atan
from math import tau as twopi
from time import sleep
from surface import *
import atexit
import mqttQualisys_sub as qtm

class event_flags:
	def __init__(self):
		self.set_flag(1)

	def set_flag(self,val=None):
		if val is not None:
			self.run_flag = val
		return self.run_flag

run_flag = event_flags()

def threadedController():
	while(run_flag.set_flag()):
		start = time()
		azThrusterLogic()
		now=time()
		diff = now-start
		sleeptime = max(0.05 - diff, 0.0)
		if (DEBUG):
			print('thread:'+str(sleeptime))
			print(run_flag.set_flag())
		sleep(sleeptime)
		#sleep(max(ticker_rate - (time()-start)),0.0)

controllerThread = Thread(target=threadedController,daemon=True)
controllerThread.start()

def exitProgram():
	print("exiting program")
	run_flag.set_flag(0)
	thrusters.exitProgram()

atexit.register(exitProgram)



joystick = xbox.Joystick()

max_speed = 400
maintain_facing=1

values = {
	'scalar1':999,
	'vector1':999,
	'scalar2':999,
	'vector2':999,
	'vector2_x2':999
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
	if (DEBUG):
		print(values)

def close():
	sleep(0.1)
	stop_thrusters_command()
	joystick.close()

def check_quit():
	returnval = 0
	if (joystick.leftBumper() and joystick.rightBumper()):
		returnval = 1
	return returnval

def check_maintain():
	global maintain_facing
	if joystick.rightTrigger():
		maintain_facing*=-1
	# print(maintain_facing)

def main():
	global max_speed, values, maintain_facing, commandQueue, valueQueue


	# redDwarf = threading.Thread(target=run,args=(commandQueue,valueQueue))
	# redDwarf.start()
	# surfaceSetup()
	maximum = max_speed / 1.2
	fail=0
	thrusters.servoboard.set_max(maximum)
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
			if (DEBUG):
				#print()
				print('f:'+str(f))
				print('o:'+str(o))
				print('s:'+str(s))
				#print()
			if (maintain_facing==1):
				# if (h==0):
					# h=999
				# heading_command(str(f))
				issueCommand('hea',f)
			else:
				# heading_command(str(999))
				issueCommand('hea',999)
			# sleep(0.05)
			if (o==0):
				o=999
			# offset_command(str(o))
			issueCommand('off',o)
			# sleep(0.05)
			if (s<10):
				s=999
			# speed_command(str(s+400))
			issueCommand('vel',s)
		surfaceLoop()
		#azThrusterLogic()
		sleep(0.01)
	close()


main()

