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


class Motion_Capture:
	def __init__(self,host_IP='192.168.5.4'):
		self.exit_state = 0
		self.connected = 0
		self.body_names=[]
		self.server = host_IP
		self.data = {}
		asyncio.run(self.setup())
	
	async def setup(self):
		self.connection = asyncio.create_task(self.connect())
		await self.connection
		await self.connected.stream_frames(components=['6deuler'], on_packet=self.on_packet)

	def run_forever(self):
		while(not self.exit_state):
		 	trash()
		 	sleep(1)
		self.connected.disconnect()

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
			print('iterations: '+str(rigbod))
			if (rigbod.text != None):
				self.body_names.append(str(rigbod.text))
				print('appended '+str(rigbod.text))
		print('body names 1: '+str(self.body_names))
		for body_name in self.body_names:
			self.data[body_name] = init_data
			print('name: '+str(body_name))
		print('body names 2: '+str(self.body_names))


	def on_packet(self,packet):
		index=packet.framenumber
		#print("Framenumber: {}".format(packet.framenumber))
		if qtm.packet.QRTComponentType.Component6dEuler in packet.components:
			#print("6D Euler Angle Packet")
			header,rigidbodies = packet.get_6d_euler()

			body_count = 0	# let them hit the floor
			for rigidbody in rigidbodies:
				if not isnan(rigidbody[0][0]):
					print('data: '+str(self.data))
					print('body_count: '+str(body_count))
					print('body_names: '+str(self.body_names))
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
		# return connection_status


if __name__ == "main":
	print('running as main')
	a = Motion_Capture('127.0.0.1')
	a.run_forever()