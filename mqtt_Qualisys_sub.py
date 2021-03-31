from time import sleep
import paho.mqtt.client as MQTT
import logging
import logging.handlers
from datetime import datetime
from gc import collect as trash
import json
import os
from server import *
from random import randint

#					   #
#-----Logging Setup-----#
#					   #
filename=default_directory + datetime.now().strftime('qtm_mqtt_%Y%m%d_%H:%M:%s.log')
log = logging.getLogger()
log.setLevel(logging.INFO)
format = logging.Formatter('%(asctime)s : %(message)s')
file_handler = logging.FileHandler(filename)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(format)
log.addHandler(file_handler)

#					   #
#-------MQTT Setup------#
#					   #
name = clientname + str(randint(1000,9999))
client=MQTT.Client(name)


# basic callback for MQTT that prints message data directly.
def print_message(client,userdata,message):
	print()
	print('mqtt rx:')
	print(message.topic)
	print(message.qos)
	print(message.payload)
	print(message.payload.decode())
	print(message.retain)
	print(client)

# A basic callback for MQTT that stores message data to a log file.
def log_message(client,userdata,message):
	#log.info('message rx')
	log.info(str(message.topic)+', '+str(message.payload))

# The callback that our program will use to control device.
def process(client,userdata,message):
	#
	# Code to use the mqtt data.
	#
	a = 1

def check_quit():
	return 1

def setup_subscription():
	check=0
	try:
		# Connect to the server (defined by server.py)
		client.connect(server)

		# Assigns the callback function when a mqtt message is received.
		if (DEBUGGING):
			# client.on_message=print_message
			client.on_message=log_message
		else:
			client.on_message=process

		# Subscribes to all the topics defined at top.
		for i in topiclist:
			client.subscribe(i+'/'+'#')

		# Start the mqtt subscription.
		client.loop_start()
		log.info('mqtt subscription script started')
		check=1
	except:
		print("didn't connect")
		log.info('mqtt subscription failed')
	return check

def main():
	q=0
	# Run the MQTT setup once.
	q=setup_subscription()

	# Because the subscription works on interrupt callbacks, nothing happens in main.
	while(q):
		trash()
		sleep(1)
		q=check_quit()

if __name__ == '__main__':
	main()




