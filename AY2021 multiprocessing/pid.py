class PID:
	# dt should be set to same as Ticker that uses this class.
	# deadzone represents the acceptable error, defaults to 0.
	def __init__(self,Kp,Ki,Kd,dt,deadzone=0):
		self.setdt(dt)
		self.setK(Kp,Ki,Kd)
		self.setDeadzone(deadzone)

	# change _dt
	def setdt(self,time):
		self._dt=time
		self.clear()
	
	# Zero out the integral
	def clearIntegral(self)	:
		self._integral=0
	
	# Zero out the last error for D gain
	def clearErrorPrevious(self):
		self._errorPrevious=0
	
	# Clear out Integral and last error
	def clear(self):
		self.clearIntegral()
		self.clearErrorPrevious()

	# Set the K values for PID, and reset the built up ID variables
	def setK(self,p,i,d):
		self._Kp = p

		self.clearIntegral()
		self._Ki = i

		self.clearErrorPrevious()
		self._Kd = d

	# Set the acceptable deadzone, "close enough"
	def setDeadzone(self,deadzone):
		self._deadzone = deadzone

	# Calculate the PID value using the error.
	def processError(self,error):
		if (abs(error) < self._deadzone):
			self.clearIntegral()
		#	self.clearErrorPrevious()

		pTerm = self._Kp * error

		self._integral+=(error * self._dt)
		iTerm = (self._Ki * self._integral)

		dTerm = (self._Kd * (error - self._errorPrevious)/self._dt)
		self._errorPrevious = error

		return (pTerm + iTerm + dTerm)

	# Calculate the PID value using a desired value against a measured value.
	def process(self,setpoint,measured):
		error=setpoint-measured
		return self.processError(error)

	# Show the current PID gains and windup values being used.
	def getParameters(self):
		parameters = {
			'Kp' : self._Kp,
			'Ki' : self._Ki,
			'Kd' : self._Kd,
			'dt' : self._dt,
			'errorPrevious' : self._errorPrevious,
			'integral' : self._integral,
			'deadzone' : self._deadzone
		}
		return parameters