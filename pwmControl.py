from pca9685 import PCA9685
import busio
from board import SCL,SDA
from time import sleep
from thruster import Thruster
import logging
import logging.handlers
from datetime import datetime

DEBUG = 1

#					   #
#-----Logging Setup-----#
#					   #
#filename = datetime.now().strftime('./log/AUV_%Y%m%d_%H:%M:%s.log')
# filename=datetime.now().strftime('/var/www/auv_logs/thrusters_%Y%m%d_%H:%M:%s.log')
# log = logging.getLogger()
# log.setLevel(logging.INFO)
# format = logging.Formatter('%(asctime)s : %(message)s')
# file_handler = logging.FileHandler(filename)
# file_handler.setLevel(logging.INFO)
# file_handler.setFormatter(format)
# log.addHandler(file_handler)

#					     #
#-----Thruster Setup-----#
#					     #
i2c = busio.I2C(SCL,SDA)				# i2c bus
servoboard = PCA9685(i2c)				# PCA9685 driver
servoboard.freq(400)					# UFrequency is universal for all channels
freq_meas = 405.6						# Based on actual measured frequency using Oscope
servoboard.cal_period(freq_meas)

# Instantiate Thrusters
fwd_port = Thruster(servoboard,0,1)	# servo ch 0
fwd_star = Thruster(servoboard,1,-1)	# servo ch 1
aft_port = Thruster(servoboard,3,-1)	# servo ch 3
aft_star = Thruster(servoboard,4,1)	# servo ch 4

def setupPCA9685():
	servoboard.reset()		# reset the servo hat
	servoboard.freq(400)	# set frequency to 400 Hz
	update(0)				# set everything to 1.5ms

def stopAllThrusters():
	fwd_port.set_speed(0)
	fwd_star.set_speed(0)
	aft_port.set_speed(0)
	aft_star.set_speed(0)


horizonLock = 0
horizonCount = 0
def EventHorizon():
	global horizonCount
	horizonLock = 1
	fwd_port.setEvent()
	fwd_star.setEvent()
	aft_port.setEvent()
	aft_star.setEvent()
	horizonCount+=1
	# log.info("Enter Event Horizon. Counts:" + str(horizonCount))


def clearHorizon():
	fwd_port.clearEvent()
	fwd_star.clearEvent()
	aft_port.clearEvent()
	aft_star.clearEvent()
	# log.info("Exit Event Horizon.")
	horizonLock = 0
	setupPCA9685()


# Passthrough functions for all 4 thrusters
def forePort(v=None):
	if v is None:
		return fwd_port.get_speed()
	elif not horizonLock:
		return fwd_port.set_speed(v)
		# update()
def foreStar(v=None):
	if v is None:
		return fwd_star.get_speed()
	elif not horizonLock:	
		return fwd_star.set_speed(v)
		# update()
def aftPort(v=None):
	if v is None:
		return aft_port.get_speed()
	elif not horizonLock:
		return aft_port.set_speed(v)
		# update()
def aftStar(v=None):
	if v is None:
		return aft_star.get_speed()
	elif not horizonLock:
		return aft_star.set_speed(v)
		# update()


thrusterFunctions = {
	'forePort':forePort,
	'foreStar':foreStar,
	'aftPort':aftPort,
	'aftStar':aftStar
}
def update(v = None):
	speeds = {}
	for key in thrusterFunctions:
		speeds[key] = thrusterFunctions[key](v)
	return speeds


def getProperties(thruster):
	n = thruster._channel
	properties = {
		'channel' : n,
		'direction' : thruster._dir,
		'period' : servoboard._period,
		'freq' : servoboard.freq(),
		'speed' : thruster.get_speed(),
		'pw' : thruster.get_pw(),
		'duty' : servoboard.duty(n),
		'pwm' : servoboard.pwm(n),
		'lock' : thruster._lock,
		'max' : servoboard.get_max(),
		'base pw' : thruster._base_pw
	}
	return properties

def freqChange(f):
	print(servoboard.freq(f))
	return update(0)

def calFreq(true_freq):
	servoboard.cal_period(true_freq)

