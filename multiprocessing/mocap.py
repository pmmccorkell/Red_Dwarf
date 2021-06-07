# Patrick McCorkell
# May 2021
# US Naval Academy
# Robotics and Control TSD
#

import qtm
import xml.etree.ElementTree as ET
from math import isnan
import asyncio
from gc import collect as trash
from time import sleep
from multiprocessing import Process, Pipe



class Motion_Capture:
	def __init__(self,communictor,host_IP='192.168.5.4'):
		self.comms = communictor
		self.exit_state = 0
		self.connected = 0
		self.body_names=[]
		self.server = host_IP
		self.data = {}

	def start(self):
		asyncio.ensure_future(self.connect())
		asyncio.get_event_loop().run_forever()

	def parseXML(self,xml):
		init_data = {
			'index':0xffff,
			'x':999,
			'y':999,
			'z':999,
			'roll':999,
			'pitch':999,
			'heading':999
		}
		root = ET.fromstring(xml)
		for rigbod in root.iter('Name'):
			# print('iterations: '+str(rigbod))
			if (rigbod.text != None):
				self.body_names.append(str(rigbod.text))
				# print('appended '+str(rigbod.text))
		# print('body names 1: '+str(self.body_names))
		for body_name in self.body_names:
			self.data[body_name] = init_data
			# print('name: '+str(body_name))
		print('Rigid Body names discovered: '+str(self.body_names))

	def on_packet(self,packet):
		index=packet.framenumber
		#print("Framenumber: {}".format(packet.framenumber))
		if qtm.packet.QRTComponentType.Component6dEuler in packet.components:
			header,rigidbodies = packet.get_6d_euler()

			body_count = 0	# let them hit the floor
			for rigidbody in rigidbodies:
				if not isnan(rigidbody[0][0]):
					# print('data: '+str(self.data))
					# print('body_count: '+str(body_count))
					# print('body_names: '+str(self.body_names))
					self.data[self.body_names[body_count]] = {
						'index':index,
						'x':rigidbody[0][0],
						'y':rigidbody[0][1],
						'z':rigidbody[0][2],
						'roll':rigidbody[1][0],
						'pitch':rigidbody[1][1],
						'heading':rigidbody[1][2]
						# 'name':self.body_names[body_count]
					}
				body_count+=1
			# self.comms.put(self.data)
			self.comms.send(self.data)
			
		else:
			print("Unidentified packet type")


	async def connect(self):

		# Make connection to Qualisys system.
		connection_status = await qtm.connect(self.server)

		if connection_status is None:
			return
		tmp = await connection_status.get_parameters(parameters=["6d"])

		self.connected = connection_status
		self.parseXML(tmp)
		
		await self.connected.stream_frames(components=['6deuler'], on_packet=self.on_packet)


server = '192.168.5.4'
server = '192.168.42.24'

def stream_data():
	global data_in
	# communicator = Queue()
	# qualisys = Motion_Capture(communicator)
	parent_pipe, child_pipe = Pipe()
	qualisys = Motion_Capture(child_pipe)
	print('start qtm process')
	data_in = {}
	mocap_process = Process(target=qualisys.start)
	
	mocap_process.start()

	while(1):
		sleep(0.001)
		# data_in = communicator.get()
		buffer={}
		while (parent_pipe.poll()):
			buffer = parent_pipe.recv()
		if buffer:
			data_in = buffer


if __name__ == '__main__':
	print('running as main')
	stream_data()