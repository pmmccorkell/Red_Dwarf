import USB_ExampleClass
import ThreeSpaceAPI
from math import pi
from time import sleep
tau = 2*pi

class YEI:
	def __init__(self,communicator):
		self.comms = communicator
		self.run = 1
		port = '/dev/ttyACM1'
		usb_comm = USB_ExampleClass.UsbCom(portName = port)
		self.sensor = ThreeSpaceAPI.ThreeSpaceSensor(usb_comm)

	def stream(self):
		self.data = {
			# 'timestamp':'nobodycares',
			'heading':777,
			'roll':777,
			'pitch':777
		}
		while(self.run):
			buffer = tuple([360/tau*x for x in self.sensor.getTaredOrientationAsEulerAngles()])
			# self.data['timestamp'] = buffer[0] # nobody cares
			self.data['pitch'] = round(buffer[1],3)
			self.data['heading'] = round(buffer[2] + 180,3)
			self.data['roll'] = round(buffer[3],3)
			self.comms.send(self.data)
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
		'timestamp':777,
		'heading':777,
		'roll':777,
		'pitch':777
	}

	buffer = {}
	while(1):
		while(yei_pipe_out.poll()):
			buffer = yei_pipe_out.recv()
		if buffer:
			# print(buffer)
			yei = buffer
			buffer = {}
		print(yei)


