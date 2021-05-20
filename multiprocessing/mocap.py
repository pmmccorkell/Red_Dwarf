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

def main(qtm_IP):
	mocap = Motion_Capture(qtm_IP)
	create_qualisys_connection = asyncio.create_task(mocap.qualisys_connect())
	[qs_conn, body_names] = await create_qualisys_connection


class Motion_Capture:
	def __init__(host_IP='192.168.5.4'):
		self.connected = 0
		self.body_names=[]
		self.server = host_IP
		self.data = {
			'heading':999,
			'roll':999,
			'pitch':999,
			'name':None,
			'x':999,
			'y':999,
			'z':999,
		}

		self.connection = asyncio.create_task(self.connect())
		await self.connection
		await self.connected.stream_frames(components=['6deuler'], on_packet=self.on_packet)
		asyncio.get_event_loop().run_forever()


	def parseXML(self,xml):
		root = ET.fromstring(xml)
		body_names=[]
		for rigbod in root.iter('Name'):
			if (rigbod.text != None):
				body_names.append(str(rigbod.text))

	def on_packet(packet):
		index=str(packet.framenumber)

	async def connect(self):

		# Make connection to Qualisys system.
		connection_status = await qtm.connect(self.server)

		if connection_status is None:
			return
		tmp = await connection_status.get_parameters(parameters=["6d"])

		self.body_names = parseXML(tmp)
		self.connected = connection_status
		
