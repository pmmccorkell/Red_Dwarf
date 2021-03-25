from pwmControl import pwmControl
from pid import PID
from time import sleep, time
from math import sin, cos
from math import tau as twopi
import logging
import logging.handlers
from datetime import datetime
from threading import Thread

DEBUG = 1

thrusters = pwmControl()

#						#
#-----Logging Setup-----#
#						#
#filename = datetime.now().strftime('./log/AUV_%Y%m%d_%H:%M:%s.log')
filename=datetime.now().strftime('/var/www/auv_logs/surface_%Y%m%d_%H:%M:%s.log')
log = logging.getLogger()
log.setLevel(logging.INFO)
format = logging.Formatter('%(asctime)s : %(message)s')
file_handler = logging.FileHandler(filename)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(format)
log.addHandler(file_handler)

############## PID Setup ##############

ticker_rate = 0.02		# seconds

az_tolerance = 2		# degrees
heading_Kp = 0.008333	
heading_Ki = 0.0		
heading_Kd = 0.0		
pidHeading = PID(heading_Kp,heading_Ki,heading_Kd,ticker_rate,az_tolerance)

# import:
######## LEAK DETECT ########

######### Intake Commands ######

 ### stop all persistent ###
persistent_heading = False 
persistent_speed = 0
persistent_offset = 0

heading = 0xffff
pitch = 0xffff
roll = 0xffff


######## Az Controller #########

def headingController():
	global persistent_heading
	speed=0
	desired_heading=persistent_heading
	current_heading=heading
	if (desired_heading != False):
		diff = abs(desired_heading-current_heading)
		if (diff>180):
			if (desired_heading>180):
				current_heading=current_heading+180
				desired_heading=desired_heading-180
			else:
				current_heading=current_heading-180
				desired_heading=desired_heading+180
		speed = pidHeading.process(desired_heading,current_heading)
	return speed

def trigSpeedController():
	global persistent_speed, persistent_offset
	desired_speed = {
		'cos' : 0,
		'sin' : 0
	}
	# convert offset to radians, and add 45deg for angled thrusters
	offset_factor = ((twopi / 360) * persistent_offset) + (twopi/8)
	
	# transform the forward speed to trig
	desired_speed['cos'] = (persistent_speed * cos(offset_factor))#/1000
	desired_speed['sin'] = (persistent_speed * sin(offset_factor))#/1000
	return desired_speed


def azThrusterLogic():
	# Get the values from each controller.
	trig_speed=trigSpeedController()
	heading_speed = headingController()

	# Form a superposition of the two controllers.
	fwd_star_speed=(trig_speed['cos'] - heading_speed)
	aft_port_speed=(trig_speed['cos'] + heading_speed)
	fwd_port_speed=(trig_speed['sin'] + heading_speed)
	aft_star_speed=(trig_speed['sin'] - heading_speed)
	if (DEBUG):
		print("azL trig:"+str(trig_speed))
		print("azL h:"+str(heading_speed))
		print("azL fw port:"+str(fwd_port_speed))
	thrusters.foreStar(fwd_star_speed)
	thrusters.aftPort(aft_port_speed)
	thrusters.forePort(fwd_port_speed)
	thrusters.aftStar(aft_star_speed)


def stopAll():
	persistent_heading = False 
	persistent_speed = 0
	persistent_offset = 0
	pidHeading.clear()
	thrusters.stopAllThrusters()

def incrementHeading(magnitude):
	heading_resolution=3	# degrees
	persistent_heading = heading+(magnitude*heading_resolution)
	pidHeading.clear()
def incrementSpeed(magnitude):
	speed_resolution=27		# us
	persistent_speed += (magniutde*speed_resolution)
def incrementOffset(magnitude):
	resolution=3	# degrees
	persistent_offset += (magnitude*heading_resolution)
increment = {
	'hea':incrementHeading,
	'vel':incrementSpeed,
	'off':incrementOffset
}
################## Put this where increment commands are intaked ########
#	increment[select](magnitude)
##################################

rangeHea = range(-180,180+1)
incrementHea = range(831,837+1)
def heaCommand(val):
	global persistent_heading
	if (DEBUG):
		print('hea cmd:'+str(val))
	if (val==999):
		persistent_heading = False
	elif (val in rangeHea):
		persistent_heading = val
	elif (val in incrementHea):
		incrementHeading(834-val)

rangeVel = range(-500,500+1)
incrementVel = range(841,847+1)
def velCommand(val):
	global persistent_speed
	if (DEBUG):
		print("vel cmd:"+str(val))
	if (val==999):
		persistent_speed=0
	elif val in rangeVel:
		persistent_speed=val
	elif val in incrementVel:
		incrementSpeed(844-val)

#rangeOff = range(-180,180+1)
rangeOff = range(0,360+1)
incrementOff = range(851,857+1)
def offCommand(val):
	global persistent_offset
	if (DEBUG):
		print("off cmd:"+str(val))
	if (val==999):
		persistent_offset=0
	elif val in rangeOff:
		persistent_offset=val
	elif val in incrementOff:
		incrementOffset(854-val)

def stopCommand(val):
	stopAll()


def hkpCommand(val):
	heading_Kp=val
def hkiCommand(val):
	heading_Ki=val
def hkdCommand(val):
	heading_Kd=val

def allClearCommand(val):
	thrusters.clearHorizon()

def horizonCommand(val):
	thrusters.EventHorizon()

commands = {
	'hea' :  heaCommand,
	'vel' :  velCommand,
	'off' :  offCommand,
	'sto' :  stopCommand,
#	'res' :  ,
#	'dep' :  ,
	'hkp' :  hkpCommand,
	'hki' :  hkiCommand,
	'hkd' :  hkdCommand,
	'clear' : allClearCommand,
	'STOP' : horizonCommand
}
def processCommand(command,value):
	commands[command](value)


commandQueue = []
valueQueue = []
def issueCommand(command,value):
	#print(command+":"+str(value))
	commandQueue.append(command)
	valueQueue.append(value)


def surfaceLoop():
	#while(checkQuit()):
	isCom = len(commandQueue)
	isVal = len(valueQueue)
	while(isCom):
		if (isCom and isVal):
			commands[commandQueue.pop(0)](valueQueue.pop(0))
			#processCommand(commandQueue.pop(0),valueQueue.pop(0))
		elif (isCom):
			commands[commandQueue.pop(0)](None)
			#processCommand(commandQueue.pop(0),None)
		isCom = len(commandQueue)

