# Patrick McCorkell
# May 2021
# US Naval Academy
# Robotics and Control TSD
#


import qtm
import xml.etree.ElementTree as ET
from math import isnan
# import asyncio
from gc import collect as trash
from time import sleep
from config import *

class Motion_Capture:
	def __init__(self):
		self.body_names=[]
		asyncio.ensure_future(self.setup())
		asyncio.get_event_loop().run_forever()

	async def setup(self):
		

##########################
	def parseXML(xml):
		root = ET.fromstring(xml)
		body_names=[]
		for rigbod in root.iter('Name'):
			if (rigbod.text != None):
				body_names.append(str(rigbod.text))

	# --------------------------------------------------------------------------
	async def qualisys_connect():
		# --------------------------------------------------------------------------

		# Make connection to Qualisys system.
		connection = await qtm.connect("192.168.5.4")

		if connection is None:
			return
		tmp = await connection.get_parameters(parameters=["6d"])

		# Saving the xml file. 
		# with open('test.xml', 'wb') as f:
		#    f.write(tmp)

		# Parse xml file to pull out rigid body names.
		# body_names = parseXML('test.xml')
		body_names = parseXML(tmp)

		return [connection, body_names]


	# --------------------------------------------------------------------------
	async def qualisys_get_info(connection, body_names, veh_name):
		# --------------------------------------------------------------------------

		# Get packet from Qualisys.
		packet = await connection.get_current_frame(components=["6deuler"])
		[header, rigid_bodies_euler] = packet.get_6d_euler()
		count = 0

		# Go through all returned rigid bodies.
		for rigid_body_euler in rigid_bodies_euler:

			# Pick out a select vehicle.
			# print(body_names[count])

			if (body_names[count]) == veh_name and not isnan(rigid_body_euler[0][0]):
				rgd_bdy_eul = rigid_body_euler

				# Get vehicle information.
				x = rgd_bdy_eul[0][0] / 1000.0
				y = rgd_bdy_eul[0][1] / 1000.0
				z = rgd_bdy_eul[0][2] / 1000.0
				hdg = np.radians(rgd_bdy_eul[1][2])
				break
			else:
				# print("Rigid body not found.")
				x = -1
				y = -1
				hdg = -1

			count = count + 1

		return [x, y, hdg]
