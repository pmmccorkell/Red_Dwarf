class Thruster:

	def setEvent(self):
		self._lock=1
		self.set_pw(self._base_pw)
	def clearEvent(self):
		self._lock=0

#	def cal_period(self,f):
#		self._period = 1000/f

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
		elif (abs(v) > self._max):
########################### Add log functionality here:
			print("max speed exceeded: "+str(v))
		else:
			# transform us to ms, and add to base 1.5 ms
			target_pw = (self._dir * v / 1000) + self._base_pw
			# current_pw = self.get_pw()
			# diff_pw = abs(target_pw-current_pw)
			# if (diff_pw > self._tolerance_pw):
			self.set_pw(target_pw)
		return self.get_speed()
	def get_speed(self):
		sp = (self.get_pw() - self._base_pw) * 1000
		return sp

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

# For test purposes
# if __name__ == "thruster": 
# 	from pca9685 import PCA9685
# 	import busio
# 	from board import SCL,SDA

# 	i2c = busio.I2C(SCL,SDA)
# 	pca = PCA9685(i2c)

# 	pca.freq(400)

# 	servo_chan = 0
# 	direction = 1

# 	thr = Thruster(pca,servo_chan,direction)
# 	print("loaded thruster.py as main")
