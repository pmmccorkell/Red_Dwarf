# Patrick McCorkell
# September 2021
# US Naval Academy
# Robotics and Control TSD
#


from adafruit_register.i2c_struct import UnaryStruct
from adafruit_register.i2c_struct_array import StructArray
from adafruit_bus_device import i2c_device

import busio
from board import SCL,SDA
from time import sleep
from json import dumps
import atexit


class Thruster:
	def __init__(self,pca,channel,direction):
		self._pca = pca						# pca9685 class
		self._channel = channel				# [0, 15] servo channel
		self._dir = direction				# [-1, 1] blade orientation
		self._lock = 0						# [0, 1] lock the thruster in safe 1.5ms
		self._max = self._pca._max			# us
		self._base_pw = 1.5					# ms
		self._tolerance_pw=0.0006			# ms
		self._period = self._pca._period	# ms
											# observed at 400Hz, +/- 1 bit in [0,4095] resolution results in precisely 0.0006000006000006497 ms difference in calculated pulsewidth

	def setEvent(self):
		self._lock=1
		self.set_pw(self._base_pw)
	def clearEvent(self):
		self._lock=0

#	def cal_period(self,f):
#		self._period = 1000/f

#	def clampESC(self,n, minn, maxn):
	def clampESC(self,n):
		minn = self._max * -1
		maxn = self._max
		return min(max(n, minn), maxn)

	def set_pw(self,val):
		if (val>self._period):
########################### Add log functionality here:
			print("max period exceeded: " + str(val))
		else:
			newduty = round((val / self._period) * 4095)
			self._pca.duty(self._channel,newduty)
	def get_pw(self):
		g_pw = self._pca.duty(self._channel)/4095 * self._period
		return g_pw

	def set_speed(self,v):
		if (self._lock == 1):
			self.set_pw(self._base_pw)
		#elif (abs(v) > self._max):
########################### Add log functionality here:
		#	print("max speed exceeded: "+str(v))
		else:
			v*self._max
			vel = self.clampESC(v)
			# transform us to ms, and add to base 1.5 ms
			target_pw = (self._dir * vel / 1000) + self._base_pw
			# current_pw = self.get_pw()
			# diff_pw = abs(target_pw-current_pw)
			# if (diff_pw > self._tolerance_pw):
			self.set_pw(target_pw)
		return self.get_speed()
	def get_speed(self):
		sp = ((self.get_pw() - self._base_pw) * 1000) / self._max
		return sp

	def update_period(self):
		self._period = self._pca._period


class PCA9685:
	REGISTER_MODE1 = UnaryStruct(0x00, "<B")
	REGISTER_PRESCALE = UnaryStruct(0xFE, "<B")
	REGISTER_PWM = StructArray(0x06, "<HH", 16)

	channels = [None] * 16

	def __init__(self, i2c, address=0x40):
		self.i2c = i2c
		self.address = address
		self.i2c_device=i2c_device.I2CDevice(i2c,address)
		self.reset()
		self.freq(400)
		self._period = 1000/self.freq()
		self._max = 400

	# def _write(self, address, value):
	# 	self.i2c.writeto_mem(self.address, address, bytearray([value]))

	# def _read(self, address):
	# 	return self.i2c.readfrom_mem(self.address, address, 1)[0]

	def reset(self):
		self.REGISTER_MODE1 = 0x00	# Mode1
		#self._write(0x00, 0x00) # Mode1

	#2020 04 03 McCorkell updated for Adafruit Issue 11
	#https://github.com/adafruit/Adafruit-PWM-Servo-Driver-Library/issues/40
	def freq(self, freq=None):
		# 25MHz / 4096 resolution = 6103.xyz
		scalar = 6103.515625
		if freq is not None:
			#Datasheet: round(25MHz / 4096 resolution / desired_frequency - 1)
			# rounding... -1 + 0.5 = - 0.5
				# return int(scalar / (self._read(0xfe) + 1)+0.5)
			prescale = int(scalar / freq - 1 + 0.5)
			old_mode = self.REGISTER_MODE1 #Mode 1
			self.REGISTER_MODE1 = (old_mode & 0x7F) | 0x10	# Mode 1, sleep
			self.REGISTER_PRESCALE = prescale
			self.REGISTER_MODE1 = old_mode # Mode 1
			sleep(0.005)
			self.REGISTER_MODE1 = old_mode | 0xA1  # Mode 1, autoincrement on
			self.set_period()
		return int(scalar / (self.REGISTER_PRESCALE + 1) + 0.5)

	def get_period(self):
		return self._period
	def set_period(self):
		self._period = (1000 / self.freq())
		return self.get_period()
	def cal_period(self,f_meas):
		if f_meas is not None:
			self._period = 1000 / f_meas
		return self.get_period()

	def set_max(self,new_max):
		if (abs(new_max)<=500):
			self._max = (new_max)
	def get_max(self):
		return self._max

	#4095 (12bit) resolution. index is pin# (0-15), 
	#on is the value [0,4096] that PWM goes high
	#off is the value [0,4096] that PWM goes low
	#special case of on=4096,off=0 --> pin is constant low
	#on=0,off=4096 --> pin is constant high
	def pwm(self, index, on=None, off=None):
		if on is None or off is None:
			# data = self.i2c.readfrom_mem(self.address, 0x06 + 4 * index, 4)
			# return struct.unpack('<HH', data)	# big endian, unsigned short
			return self.REGISTER_PWM[index]
		# data = struct.pack('<HH', on, off)		# big endian, unsigned short

		#define LED0_ON_L 0x6		
		#define LED0_ON_H 0x7	On 0xH + 0xL --> delay to turn on (out of 4095)
		#define LED0_OFF_L 0x8
		#define LED0_OFF_H 0x9	Off 0xH + 0xL --> delay to turn off (out of 4095)
			#absolute count, not relative to on
		self.REGISTER_PWM[index] = (on,off)

	def duty(self, index, value=None, invert=False):
		if value is None:
			pwm = self.pwm(index)
			if pwm == (0, 4096):
				value = 0
			elif pwm == (4096, 0):
				value = 4095
			value = pwm[1]
			if invert:
				value = 4095 - value
			return value
		if not 0 <= value <= 4095:
			raise ValueError("Out of range")
		if invert:
			value = 4095 - value
		if value == 0:
			self.pwm(index, 0, 4096)
		elif value == 4095:
			self.pwm(index, 4096, 0)
		else:
			self.pwm(index, 0, value)

	def zeroout(self):
		for i in range(16):
			#print('turning off channel '+str(i))
			self.pwm(i,0,4096)

	def __exit__(self, exception_type, exception_value, traceback):
		self.zeroout()
		self.reset()
		print("pca9685 uninitialized")



class pwmControl:
	#					     #
	#-----Thruster Setup-----#
	#					     #
	def __init__(self):
		self.horizonLock = 0
		self.horizonCount = 0
		i2c = busio.I2C(SCL,SDA)				# i2c bus
		self.servoboard = PCA9685(i2c)			# PCA9685 driver
		self.servoboard.freq(400)				# Frequency is universal for all channels

		# Instantiate Thrusters
		# Pass the pca9685 class, servo channel #, and direction of the blades.
		self.fwd_port = Thruster(self.servoboard,0,1)	# servo ch 0
		self.fwd_star = Thruster(self.servoboard,1,-1)	# servo ch 1, blades reversed
		self.aft_port = Thruster(self.servoboard,3,-1)	# servo ch 3, blades reversed
		self.aft_star = Thruster(self.servoboard,4,1)	# servo ch 4
		self.test_thruster = Thruster(self.servoboard,15,1) # for test purposes
		self.thruster_objects = {
			'fwd_port':self.fwd_port,
			'fwd_star':self.fwd_star,
			'aft_port':self.aft_port,
			'aft_star':self.aft_star,
			'test_thruster':self.test_thruster
		}
		self.thrusterFunctions = {
			'forePort':self.forePort,
			'foreStar':self.foreStar,
			'aftPort':self.aftPort,
			'aftStar':self.aftStar,
			'testThruster':self.testThruster
		}
		self.stopAllThrusters()


	def setupPCA9685(self):
		self.servoboard.reset()		# reset the servo hat
		self.servoboard.freq(400)	# set frequency to 400 Hz
		self.update(0)				# set everything to 1.5ms

	def stopAllThrusters(self,v=None):
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
	def testThruster(self,v=None):
		if v is None:
			return self.test_thruster.get_speed()
		elif not self.horizonLock:
			return self.test_thruster.set_speed(v)
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

	def change_freq(self,f):
		print(self.servoboard.freq(f))
		for key in self.thruster_objects:
			#print(key)
			print(self.thruster_objects[key].update_period())
		return self.update(0)

	def exitProgram(self):
		self.stopAllThrusters()
		sleep(2)
		self.servoboard.zeroout()
		print(self)

	def __exit__(self):
		self.exitProgram()

	# Return a string of thruster data for MQTT stuff later
	def __str__(self):
		return dumps(self.update())
	def __repr__(self):
		return self.__str__()

def update_pwm(speed):
	global thrusters
	print(speed)
	print(thrusters.update(speed))

def clampyclamp(self,minn,maxn,n):
	return min(max(n, minn), maxn)

def run():
	global thrusters
	thrusters = pwmControl()
	v = 0
	direction=1
	cycle=0
	max_val=thrusters.servoboard._max
	while(1):
		if v>=max_val:
			update_pwm(max_val)
			sleep(1.5)
			direction=-1
		elif v<=(-1*max_val):
		#	update_pwm(1)
		#	sleep(3)
			update_pwm(-1*max_val)
			sleep(1.5)
			direction=1
			cycle+=1
		if cycle==2:
			update_pwm(0)
			# update_pwm(1)
			sleep(3)
			cycle=0
		v+=direction*4
		update_pwm(v)
		sleep(0.003)

def exit_program():
	print("exiting program")
	thrusters.exitProgram()

atexit.register(exit_program)

if __name__ == '__main__':
	print("running as main")
	run()
