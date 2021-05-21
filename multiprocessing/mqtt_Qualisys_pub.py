# Patrick McCorkell
# March 2021
# US Naval Academy
# Robotics and Control TSD

import json
from time import sleep
from datetime import datetime
import paho.mqtt.client as MQTT
from gc import collect as trash
import asyncio
import qtm
import xml.etree.ElementTree as ET
from config import *
from random import randint
from math import isnan

name=pub_clientname+str(randint(1000,9999))
client = MQTT.Client(name)
topic_prefix = 'QTM/'

# initialize global array of publish topics (will be appended with rigid body names)
pub_topics = [
	'timestamp'
	]

def parseXML(xml):
	global pub_topics
	root = ET.fromstring(xml)

	for rigbod in root.iter('Name'):
		if (rigbod.text != None):
			print(rigbod.text)
			pub_topics.append(str(rigbod.text))
	print(pub_topics)

def parseXML_file(xmlfile): 
	global pub_topics  
	# create element tree object 
	tree = ET.parse(xmlfile)
  
	# get root element 
	root = tree.getroot()
	
	# find the names of all the body elements
	for rigbod in root.iter('Name'):
		# append rigid body names to publish topic list
		if (rigbod.text != None):
			print(rigbod.text)
			pub_topics.append(str(rigbod.text))
	print(pub_topics)
	# TODO: What to do if it returns no rigid bodies


#function definition
def on_packet(packet):
	''' Callback function that is called everytime a data packet arrives from QTM '''
	global pub_topics
	index=str(packet.framenumber)
	#print("Framenumber: {}".format(packet.framenumber))
	if qtm.packet.QRTComponentType.Component6d in packet.components:
		#print("6D Packet\n")
		[header, bodies] = packet.get_6d()
		#print("Component info: {}".format(header))
		#print(type(bodies))
		count = 1
		for body in bodies:
			msg_pos = {'index':index,'x':str(body[0][0]),'y':str(body[0][1]),'z':str(body[0][2])}
			msg_ortn = {'index':index,'R':body[1][0]}
			print("\t\n",pub_topics[count]+'/'+'position',msg_pos,'\t\n')
			print("\t\n",pub_topics[count]+'/'+'orientation',msg_ortn,'\t\n')
			client.publish(topic_prefix+pub_topics[count]+'/'+'position',json.dumps(msg_pos))
			client.publish(topic_prefix+pub_topics[count]+'/'+'orientation',json.dumps(msg_ortn))
			count = count+1
	elif qtm.packet.QRTComponentType.Component6dEuler in packet.components:
		#print("6D Euler Angle Packet")
		header,bodies = packet.get_6d_euler()
		count = 1
		for body in bodies:
			if not isnan(body[0][0]):
				msg_pos = {'index':index,'x':str(body[0][0]),'y':str(body[0][1]),'z':str(body[0][2])}
				msg_ortn = {'index':index,'r':body[1][0],'p':body[1][1],'h':body[1][2]}
				#print("\t\n",topic_prefix+pub_topics[count]+'/'+'position',msg_pos,'\t\n')
				#print("\t\n",topic_prefix+pub_topics[count]+'/'+'orientation',msg_ortn,'\t\n')
				client.publish(topic_prefix+pub_topics[count]+'/'+'position',json.dumps(msg_pos))
				client.publish(topic_prefix+pub_topics[count]+'/'+'orientation',json.dumps(msg_ortn))
			count = count+1
	else:
		print("Unidentified packet type")

async def setup():
	''' Main function '''
	# Connect to MQTT Broker
	try:
			client.connect(mqtt_broker)
			print("Connected to MQTT broker: "+mqtt_broker)
	except:
			print("didn't connect to "+mqtt_broker)

	# Connect to QTM Server
	connection = await qtm.connect(qtm_server)
	print('connection: '+str(connection))
	if connection is None:
		print('returning')
		return

	# Pull Session parameters from QTM, includes rigid body names
	tmp = await connection.get_parameters(parameters=['6d'])
	parseXML(tmp)
	print(tmp)

	# saving the xml file, for examination and instructional  purposes.
	#with open('params6D.xml', 'wb') as f: 
	#	f.write(tmp)

	# Parse xml file to pull out rigid body names
	#parseXML_file('params6D.xml')
		
	await connection.stream_frames(components=['6deuler'], on_packet=on_packet)


if __name__ == '__main__':
	asyncio.ensure_future(setup())
	asyncio.get_event_loop().run_forever()

	# setup()
	# while(1):
	#	 sleep(1)
	#	 trash()

