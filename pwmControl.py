from pca9685 import PCA9685
import busio
from board import SCL,SDA
from time import sleep, time
from thruster import Thruster
from json import dumps
from pca9685config import *

class pwmControl:
	#					     #
	#-----Thruster Setup-----#
	#					     #
	def __init__(self):
		self.horizonLock = 0
		self.horizonCount = 0
		i2c = busio.I2C(SCL,SDA)				# i2c bus
		self.servoboard = PCA9685(i2c)				# PCA9685 driver
		self.servoboard.freq(400)					# UFrequency is universal for all channels
		#freq_meas = 405.6						# Based on actual measured frequency using Oscope
		self.servoboard.cal_period(freq_meas)

		# Instantiate Thrusters
		self.fwd_port = Thruster(self.servoboard,0,1)	# servo ch 0
		self.fwd_star = Thruster(self.servoboard,1,-1)	# servo ch 1
		self.aft_port = Thruster(self.servoboard,3,-1)	# servo ch 3
		self.aft_star = Thruster(self.servoboard,4,1)	# servo ch 4
		self.thrusterFunctions = {
			'forePort':self.forePort,
			'foreStar':self.foreStar,
			'aftPort':self.aftPort,
			'aftStar':self.aftStar
		}
		self.setupPCA9685()



	def setupPCA9685(self):
		self.servoboard.reset()		# reset the servo hat
		self.servoboard.freq(400)	# set frequency to 400 Hz
		self.update(0)				# set everything to 1.5ms

	def stopAllThrusters(self):
		self.update(0)
		# print("stopped all thrusters")


	def EventHorizon(self):
		self.horizonLock = 1
		self.fwd_port.setEvent()
		self.fwd_star.setEvent()
		self.aft_port.setEvent()
		self.aft_star.setEvent()
		self.horizonCount+=1
		# log.info("Enter Event Horizon. Counts:" + str(horizonCount))


	def clearHorizon(self):
		self.fwd_port.clearEvent()
		self.fwd_star.clearEvent()
		self.aft_port.clearEvent()
		self.aft_star.clearEvent()
		# log.info("Exit Event Horizon.")
		self.horizonLock = 0
		self.setupPCA9685()


	# Passthrough functions for all 4 thrusters
	def forePort(self,v=None):
		if v is None:
			return self.fwd_port.get_speed()
		elif not self.horizonLock:
			return self.fwd_port.set_speed(v)
			# update()
	def foreStar(self,v=None):
		if v is None:
			return self.fwd_star.get_speed()
		elif not self.horizonLock:	
			return self.fwd_star.set_speed(v)
			# update()
	def aftPort(self,v=None):
		if v is None:
			return self.aft_port.get_speed()
		elif not self.horizonLock:
			return self.aft_port.set_speed(v)
			# update()
	def aftStar(self,v=None):
		if v is None:
			return self.aft_star.get_speed()
		elif not self.horizonLock:
			return self.aft_star.set_speed(v)
			# update()


	def update(self,v = None):
		speeds = {}
		for key in self.thrusterFunctions:
			speeds[key] = self.thrusterFunctions[key](v)
		return speeds


	def getProperties(self,thruster):
		n = thruster._channel
		properties = {
			'channel' : n,
			'direction' : thruster._dir,
			'period' : self.servoboard._period,
			'freq' : self.servoboard.freq(),
			'speed' : thruster.get_speed(),
			'pw' : thruster.get_pw(),
			'duty' : self.servoboard.duty(n),
			'pwm' : self.servoboard.pwm(n),
			'lock' : thruster._lock,
			'max' : self.servoboard.get_max(),
			'base pw' : thruster._base_pw
		}
		return properties

	def freqChange(self,f):
		print(self.servoboard.freq(f))
		return self.update(0)

	def calFreq(self,true_freq):
		self.servoboard.cal_period(true_freq)

	# Return a string of thruster data for MQTT stuff later
	def __str__(self):
		return dumps(self.update())
	def __repr__(self):
		return self.__str__()

	def exitProgram(self):
		self.stopAllThrusters()
		sleep(2)
		self.servoboard.zeroout()
		print(self)

	
