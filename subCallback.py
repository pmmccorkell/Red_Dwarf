import paho.mqtt.client as MQTT
from random import randint
from json import dumps, loads
from math import pi as pie
from cmath import exp as trueExp
from server import *
from datetime import datetime
from gc import collect as trash
import logging
import logging.handlers
from time import sleep

heading_meas = 0xffff

#					   #
#-----Logging Setup-----#
#					   #
# filename=default_directory + datetime.now().strftime('qtm_mqtt_%Y%m%d_%H:%M:%s.log')
# log = logging.getLogger()
# log.setLevel(logging.INFO)
# format = logging.Formatter('%(asctime)s : %(message)s')
# file_handler = logging.FileHandler(filename)
# file_handler.setLevel(logging.INFO)
# file_handler.setFormatter(format)
# log.addHandler(file_handler)


############################################################
################# MQTT CONNECTION HANDLING #################
############################################################

is_connected=0

clientname += str(randint(1000,9999))
client=MQTT.Client(clientname)



# Break connection to MQTT broker.
# Called from within Matlab to properly deconstruct MQTT client.
def mqttTerminate():
	global client
	client.loop_stop()
	client.disconnect()
	is_connected=0
	print("Terminated python MQTT")


#####################################################################
####################### SUBSCRIPTION CALLBACK #######################
#####################################################################

# Redirect from MQTT callback function.
# Error checking.
def defaultFunction(whatever):
	print("PYTHON >> Discarding. No filter for topic "+str(whatever.topic)+" discovered.")

# Redirect from MQTT callback function when no action is required.
def dontdonothing():
	lennon=1j
	nothingtoseehere=trueExp(lennon*pie)
	print(nothingtoseehere)

# A basic callback for MQTT that stores message data to a log file.
def log_message(message):
	print(str(message.topic)+', '+str(message.payload))
# 	#log.info('message rx')
# 	log.info(str(message.topic)+', '+str(message.payload))

def orientation(message):
	global heading_meas
	heading_meas = -1 * loads(message.payload.decode())['h']
	# print('hea: '+str(heading))


# Dictionary used to store function() locations.
# MQTT topics are the keys, and they're associated to the 
# respective function location to be executed for that topic.
subscription_topics={
	'timestamp':log_message,
    'QTM/RedDwarf/orientation':orientation
}


# Callback for MQTT subscriptions.
# Called as Interrupt by paho-mqtt when a subscribed topic is received.
# 
def callback_handler(client,userdata,message):
	################# EXAMPLE START ##################
	# print(message.payload.decode())
	# print(message.topic)
	# msg=message.payload.decode().lower()
	# if (msg.topic == 'OptiTrack/Control/AddObject'):
		# AddObject(message)
	################# EXAMPLE END ####################
	
	# Get the function associated to the MQTT topic.
	# load the defaultFunction if an associated topic is not found.
	topicFunction = subscription_topics.get(message.topic,defaultFunction)
	
	# Execute the function associated to the MQTT topic, 
	# passing the MQTT message.
	topicFunction(message)

# Connect to MQTT broker.
def mqtt_connect():
	global client, is_connected

	# Unique clientname. Random element to prevent collisions during
	# frequent reconnections, outages, intermittent issues, etc.
	

	# Only connect if not already connected.
	if not is_connected:
		client.connect(server)
		client.loop_start()
		print("Connected to "+server)
		# log.info('mqtt subscription script started')
		is_connected=1
	
	client.on_message = callback_handler
	for k in subscription_topics:
		client.subscribe(k)



############################################################
###################### DEBUGGING ###########################
############################################################

# Topics for Debugger to subscribe to.
# Global so user can edit list w/o reloading script.
debugTopics = ['QTM/#','OptiTrack/Control/#','test']

# Passthrough for debugging in Python environment.
def debugSubscription():
	global client, buffer

	# Create a global dummy buffer to simulate a RigidBody object from Matlab.
	buffer = {'Name': 'vroom', 'FrameIndex': 33386087, 'TimeStamp': 531712.59596601, 'FrameLatency': 1.2978, 'isTracked': True, 'Position': [-555.4297566413879, 1133.2718133926392, 580.9705853462219], 'Quaternion': [-0.9823990057235511, 0.03210517614039003, -0.04536310217498993, 0.17833529490184152], 'Rotation': [[0.9322774120833481, -0.35330567107334326, -0.07767837348058937], [0.34748010858269623, 0.9343315498255698, -0.07925988354714225], [0.10058032142786663, 0.04690050946379489, 0.9938228922466537]], 'HgTransform': [[0.9322774120833481, -0.35330567107334326, -0.07767837348058937, -555.4297566413879], [0.34748010858269623, 0.9343315498255698, -0.07925988354714225, 1133.2718133926392], [0.10058032142786663, 0.04690050946379489, 0.9938228922466537, 580.9705853462219], [0, 0, 0, 1]], 'MarkerPosition': [[-534.112811088562, -585.0552916526794, -547.1159219741821], [1073.0293989181519, 1132.2520971298218, 1194.5387125015259], [574.7097134590149, 585.7723355293274, 582.3908448219299]], 'MarkerSize': [12.136011384427547, 15.373353846371174, 11.472992599010468]}

	# client.on_message=MESSAGE_CALLBACK
	mqtt_connect()
	# Setup MQTT connection
	# client.on_message=MESSAGE_CALLBACK
	client.on_message = callback_handler

	# Subscribe to topics
	for topic in debugTopics:
		client.subscribe(topic)
		print("Subscribed to: " + topic)

# Sample. Not used. Available to reroute Debugging Subscriber here.
def MESSAGE_CALLBACK(client,userdata,message):
	print()
	print("mqtt rx:")
	print(message.topic)
	print(message.qos)
	print(message.payload)
	print(message.payload.decode())
	print(message.retain)
	print(client)

# If this script is being called directly, it's gonna need 
# its own MQTT subscription service.
if __name__ == "__main__":
	mqtt_connect()
	while(1):
		print(heading_meas)
		sleep(1)


