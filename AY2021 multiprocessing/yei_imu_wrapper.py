import USB_ExampleClass
# from ThreeSpaceAPI import *
import ThreeSpaceAPI
from math import pi
tau = 2*pi

# com = USB_ExampleClass.UsbCom()
# sensor = ThreeSpaceSensor(com)

# --> enter /dev/ttyS21

# reading = tuple([360/tau*x for x in sensor.getTaredOrientationAsEulerAngles()])

# sensor.cleanup()

# - create a container for this
# - create a pipe to get latest vals
# - integrate into log
# - integrate into graph ?


class YEI:
	def __init__(self,communicator):
		self.comms = communicator
		self.run = 1
		port = '/dev/ttyACM1'
		usb_comm = USB_ExampleClass.UsbCom(portName = port)
		self.sensor = ThreeSpaceAPI.ThreeSpaceSensor(usb_comm)


	def stream(self):
		while(self.run):

