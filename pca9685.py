# import struct
from time import sleep
from adafruit_register.i2c_struct import UnaryStruct
from adafruit_register.i2c_struct_array import StructArray
from adafruit_bus_device import i2c_device

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
