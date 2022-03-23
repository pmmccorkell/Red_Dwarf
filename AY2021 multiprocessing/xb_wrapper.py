# Patrick McCorkell
# May 2021
# US Naval Academy
# Robotics and Control TSD
#

from xbox import Joystick
from time import sleep

class XBoxController:
	def __init__(self,communicator):
		self.comms = communicator
		self.joystick = Joystick(100)

	def poll(self):
		while(1):
			self.joystick.refresh()
			self.comms.send(self.joystick.reading)
			sleep(0.008)
