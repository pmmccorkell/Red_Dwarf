# Patrick McCorkell
# March 2021
# US Naval Academy
# Robotics and Control TSD
#

from pwmControl import pwmControl
from pid import PID
from time import sleep, time
from math import sin, cos
from math import tau as twopi
import logging
import logging.handlers
from datetime import datetime

#						#
#-----Logging Setup-----#
#						#
#filename = datetime.now().strftime('./log/AUV_%Y%m%d_%H:%M:%s.log')
filename=datetime.now().strftime('/logs/auv_logs/surface_%Y%m%d_%H:%M:%s.log')
log = logging.getLogger()
log.setLevel(logging.INFO)
format = logging.Formatter('%(asctime)s : %(message)s')
file_handler = logging.FileHandler(filename)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(format)
log.addHandler(file_handler)


class Controller():
	def __init__(self):
		self.DEBUG = 0

		self.thrusters = pwmControl()


		############## PID Setup ##############

		self.ticker_rate = 0.02		# seconds

		self.az_tolerance = 2		# degrees
		self.heading_Kp = 0.08333	
		self.heading_Ki = 0.0		
		self.heading_Kd = 0.0		
		self.pidHeading = PID(self.heading_Kp,self.heading_Ki,self.heading_Kd,self.ticker_rate,self.az_tolerance)

		# import:
		######## LEAK DETECT ########

		######### Intake Commands ######

		### stop all persistent ###
		self.persistent_heading = False 
		self.persistent_speed = 0
		self.persistent_offset = 0

		self.heading = 0xffff
		self.pitch = 0xffff
		self.roll = 0xffff

		self.rangeHea = range(-180,180+1)
		self.incrementHea = range(831,837+1)
		self.rangeVel = range(-500,500+1)
		self.incrementVel = range(841,847+1)

		#self.rangeOff = range(-180,180+1)
		self.rangeOff = range(0,360+1)
		self.incrementOff = range(851,857+1)

		self.commands = {
			'hea' :  self.heaCommand,
			'vel' :  self.velCommand,
			'off' :  self.offCommand,
			'sto' :  self.stopCommand,
		#	'res' :  ,
		#	'dep' :  ,
			'hkp' :  self.hkpCommand,
			'hki' :  self.hkiCommand,
			'hkd' :  self.hkdCommand,
			'clear' : self.allClearCommand,
			'STOP' : self.horizonCommand
		}

		self.commandQueue = []
		self.valueQueue = []


		# self.increment = {
		# 	'hea':incrementHeading,
		# 	'vel':incrementSpeed,
		# 	'off':incrementOffset
		# }
		################## Put this where increment commands are intaked ########
		#	increment[select](magnitude)
		##################################


######## Az Controller #########

	def headingController(self):
		speed=0
		desired_heading=self.persistent_heading
		current_heading=self.heading
		if (desired_heading != False):
			diff = abs(desired_heading-current_heading)
			if (diff>180):
				if (desired_heading>180):
					current_heading=current_heading+180
					desired_heading=desired_heading-180
				else:
					current_heading=current_heading-180
					desired_heading=desired_heading+180
			speed = self.pidHeading.process(desired_heading,current_heading)
		return speed

	def trigSpeedController(self):
		desired_speed = {
			'cos' : 0,
			'sin' : 0
		}
		# convert offset to radians, and add 45deg for angled thrusters
		offset_factor = ((twopi / 360) * self.persistent_offset) + (twopi/8)
		
		# transform the forward speed to trig
		desired_speed['cos'] = (self.persistent_speed * cos(offset_factor))#/1000
		desired_speed['sin'] = (self.persistent_speed * sin(offset_factor))#/1000
		return desired_speed


	def azThrusterLogic(self):
		# Get the values from each controller.
		trig_speed=self.trigSpeedController()
		heading_speed = self.headingController()

		# Form a superposition of the two controllers.
		fwd_star_speed=(trig_speed['cos'] - heading_speed)
		aft_port_speed=(trig_speed['cos'] + heading_speed)
		fwd_port_speed=(trig_speed['sin'] + heading_speed)
		aft_star_speed=(trig_speed['sin'] - heading_speed)
		if (self.DEBUG):
			print("azL trig:"+str(trig_speed))
			print("azL h:"+str(heading_speed))
			print("azL fw port:"+str(fwd_port_speed))
		self.thrusters.foreStar(fwd_star_speed)
		self.thrusters.aftPort(aft_port_speed)
		self.thrusters.forePort(fwd_port_speed)
		self.thrusters.aftStar(aft_star_speed)


	def stopAll(self):
		self.persistent_heading = False 
		self.persistent_speed = 0
		self.persistent_offset = 0
		self.pidHeading.clear()
		self.thrusters.stopAllThrusters()

	def incrementHeading(self,magnitude):
		heading_resolution=3	# degrees
		self.persistent_heading = heading+(magnitude*heading_resolution)
		self.pidHeading.clear()
	def incrementSpeed(self,magnitude):
		speed_resolution=27		# us
		self.persistent_speed += (magniutde*speed_resolution)
	def incrementOffset(self,magnitude):
		resolution=3	# degrees
		self.persistent_offset += (magnitude*resolution)

	def heaCommand(self,val):
		if (self.DEBUG):
			print('hea cmd:'+str(val))
		if (val==999):
			self.persistent_heading = False
		elif (val in self.rangeHea):
			self.persistent_heading = val
		elif (val in self.incrementHea):
			self.incrementHeading(834-val)

	def velCommand(self,val):
		if (self.DEBUG):
			print("vel cmd:"+str(val))
		if (val==999):
			self.persistent_speed=0
		elif val in self.rangeVel:
			self.persistent_speed=val
		elif val in self.incrementVel:
			self.incrementSpeed(844-val)

	def offCommand(self,val):
		if (self.DEBUG):
			print("off cmd:"+str(val))
		if (val==999):
			self.persistent_offset=0
		elif val in self.rangeOff:
			self.persistent_offset=val
		elif val in incrementOff:
			self.incrementOffset(854-val)

	def stopCommand(self,val):
		self.stopAll()


	def hkpCommand(self,val):
		self.heading_Kp=val
	def hkiCommand(self,val):
		self.heading_Ki=val
	def hkdCommand(self,val):
		self.heading_Kd=val

	def allClearCommand(self,val):
		self.thrusters.clearHorizon()

	def horizonCommand(self,val):
		self.thrusters.EventHorizon()

	def processCommand(self,command,value):
		self.commands[command](value)


	def issueCommand(self,command,value):
		#print(command+":"+str(value))
		self.commandQueue.append(command)
		self.valueQueue.append(value)


	def surfaceLoop(self):
		#while(checkQuit()):
		isCom = len(self.commandQueue)
		isVal = len(self.valueQueue)
		while(isCom):
			if (isCom and isVal):
				self.commands[self.commandQueue.pop(0)](self.valueQueue.pop(0))
				#processCommand(commandQueue.pop(0),valueQueue.pop(0))
			elif (isCom):
				self.commands[self.commandQueue.pop(0)](None)
				#processCommand(commandQueue.pop(0),None)
			isCom = len(self.commandQueue)

