import USB_ExampleClass
# from ThreeSpaceAPI import *
import ThreeSpaceAPI
from math import pi
from time import sleep
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
		data = {
			'timestamp':999,
			'heading':999,
			'roll':999,
			'pitch':999
		}
		while(self.run):
			buffer = tuple([360/tau*x for x in self.sensor.getTaredOrientationAsEulerAngles()])
			data['timestamp'] = buffer[0]
			data['heading'] = buffer[1]
			data['roll'] = buffer[2]
			data['pitch'] = buffer[3]
			self.comms.send(data)
			sleep(0.01)

	def close(self):
		self.run = 0


if __name__ == '__main__':
	print("running as main")
	from multiprocessing import Process, Pipe
	daemon_mode = True

	yei_pipe_in, yei_pipe_out = Pipe()
	print("initiating YEI imu")
	yei_imu = YEI(yei_pipe_in)
	print("start process")
	yei_process = Process(target=yei_imu.stream,daemon=daemon_mode)
	yei_process.start()

	yei = {
		'timestamp':999,
		'heading':999,
		'roll':999,
		'pitch':999
	}

	buffer = {}
	while(1):
		while(yei_pipe_out.poll()):
			buffer = yei_pipe_out.recv()
		if buffer:
			print(buffer)
			yei = buffer
			buffer = {}
		# print(yei)


