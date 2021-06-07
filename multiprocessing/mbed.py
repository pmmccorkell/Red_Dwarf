# Patrick McCorkell
# April 2021
# US Naval Academy
# Robotics and Control TSD
#


import time
import serial
import logging
import logging.handlers
from datetime import datetime
import RPi.GPIO as GPIO
import json
import os

DEBUG = 1

#					   #
#------Serial Setup-----#
#					   #
ser=serial.Serial(
	port='/dev/ttyACM0',
	baudrate=115200,
	parity=serial.PARITY_NONE,
	stopbits=serial.STOPBITS_ONE,
	bytesize=serial.EIGHTBITS,
	timeout=1
	)

#					   #
#-----Logging Setup-----#
#					   #
#filename = datetime.now().strftime('./log/AUV_%Y%m%d_%H:%M:%s.log')
filename=datetime.now().strftime('/var/www/auv_logs/AUV_%Y%m%d_%H:%M:%s.log')
log = logging.getLogger()
log.setLevel(logging.INFO)
format = logging.Formatter('%(asctime)s : %(message)s')
file_handler = logging.FileHandler(filename)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(format)
log.addHandler(file_handler)


logline='KEY: heading:|:roll:|:pitch:|:BNO cal:|:status'
log.info(logline)

#					   #
#-----PHP Interfacing-----#
#					   #
# overlay = "/dev/shm/mjpeg/user_annotate.txt"
# os.system("sudo chmod 777 /dev/shm/mjpeg/user_annotate.txt")
# serial_data_directory = "/var/www/html/"


def clear_serial():
	ser.reset_input_buffer()
	time.sleep(0.01)
	try:
		ser.readline()
		return 1
	except UnicodeDecodeError:
		return 0


def reset_mbed():
	#print("Restarting mbed")
	#print("Program may exit due to serial reset")
	#Set Event flag to end serial read thread.
	stop_threads.set()
	#print("Shutting down thrusters and closing serial link.")
	time.sleep(2)
	ser.send_break()	 #break command over serial resets mbed
	writeline=('res:000').encode()
	time.sleep(0.1)
	ser.write(writeline)
	log.info("Raspi command sent: "+writeline.decode())
	#print("sent: "+writeline.decode())
	#print("Restarting serial link.")
	#clear Event flags.
	stop_threads.clear()
	for i in range(100):
		serialreset=0
		while (serialreset==0):
			serialreset=clear_serial()

	#Start reading from serial again.
	start_serial_thread()
	return 1

#For error handling
#ensure user input is int or str before using logic
def isInt(string):
	try: 
		int(string)
		return True
	except ValueError:
		return False
		
def isHex(string):
	try:
		int(string,base=16)
		return True
	except ValueError:
		return False

# def video_overlay():
# 	nl="\n"
# 	cal_data=str(hex(calibration))
# 	status_data=str(hex(status))
# 	bno_pos=str(status & 0x0007)

# 	h = round(heading,1)
# 	r = round(roll,1)
# 	p = round(pitch,1)
# 	ann1=("h: "+str(h)+", r: "+str(r)+", p: "+str(p))
# 	ann2=("cal: "+cal_data+", pos: "+bno_pos)
# 	annotate = open(overlay, 'w')
# 	annotate.write("\n" + ann1 + nl + ann2)
# 	annotate.close()

# 	#data_stream=("ser_h "+str(h)+nl+"ser_r "+str(r)+nl+"ser_p "+str(p)+nl+"ser_d "+str(d)+nl+"ser_port "+p_pw+nl+"ser_stbd "+s_pw+nl+"ser_fwd "+f_pw+nl+"ser_aft "+a_pw+nl+"ser_cal "+cal_data+nl+"ser_bno "+bno_pos)
# 	#serial_data = open(serial_data_file, 'w')
# 	#serial_data.write(data_stream)
# 	#serial_data.close()
# 	json_data={'ser_h':str(h), 'ser_r':str(r), 'ser_p':str(p), 'ser_d':str(d), 'ser_cal':cal_data, 'ser_status':status_data}
# 	serial_data_file = open(serial_data_directory+"serial_JSON", 'w')
# 	#serial_data.write(ser_h)
# 	json.dump(json_data,serial_data_file)
# 	serial_data_file.close()

def shutdownPi():
	log.info("Water leak detected. All systems shutdown.")
	os.system("sudo shutdown -h now")
	log.info("Shutdown for water leak failed. The show goes on.")

def get_angles():
	#Set key values.
	#Keys are first 4 Hexadecimal values in line
	#and used to "tag" what kind of data follows
	ver_key=0x1234
	status_key=0xffff  #also 'ready'
	cal_key=0xc000
	h_key=0xc100
	r_key=0xc300
	p_key=0xc500

	#Set globals accessible outside this thread
	global status
	global calibration
	global heading
	global roll
	global pitch
	global depth

	#Initialize values to 0
	status,calibration,heading,roll,pitch,depth=0,0,0,0,0,0
	port_pw,starboard_pw,fore_pw,aft_pw=0,0,0,0
	horizon_count,horizon_state=0,0
	key,st,cal,h,r,p,d=0x0,0x0,0x0,0x0,0x0,0x0,0x0
	
	#See mbed code. Roll and Pitch are +/- 180 from BNO
	#Offset allows mbed and raspi to deal strictly with
	#positive numbers.
	#360 deg added on mbed side, must be subtracted
	offset=0x1680

	#mbed sends 8bit words, +1 for overhead
	word_size=9

	#mbed sends 11 8bit words every 20ms
	#Or one word around every 2ms
	#This while loop only processes 1 word at a time

	#Only proceed if there are bytes in Serial waiting to be read
	while (ser.inWaiting==0):
		time.sleep(0.005)
		#print("no serial input... waiting")

	#Read bytes from Serial
	in_buffer=ser.readline()

	if DEBUG:
		print(in_buffer)
		print(len(in_buffer))
	
	#Only assign prefix and data if serial line is correct length
	#Prevents Value Errors
	int_buffer_prefix=0x10000
	int_buffer_data=0x10000
	length=len(in_buffer)
	if (length==word_size):
		str_buffer_prefix=in_buffer[0:2].decode()+in_buffer[2:4].decode()
		##print("prefix: "+str(str_buffer_prefix))
		if isHex(str_buffer_prefix):
			int_buffer_prefix=int(str_buffer_prefix,base=16)
		str_buffer_data=in_buffer[4:6].decode()+in_buffer[6:8].decode()
		##print("str prefix: " + str(str_buffer_prefix)+ ", data: "+str(str_buffer_data))
		if isHex(str_buffer_data):
			int_buffer_data=int(str_buffer_data,base=16)
		##print("int prefix: " + str(hex(int_buffer_prefix)) + ", data: " + str(hex(int_buffer_data)))
	
		if DEBUG:
			print(int_buffer_prefix)
			print(int_buffer_data)

	elif (in_buffer[0:3].decode()=='log'):
		log.info(in_buffer[0:(length-2)].decode())
	else:
		log.debug(in_buffer[0:(length-2)].decode())

	#Sort data to correct variable using the keys
	if (int_buffer_prefix == ver_key):
		key=int_buffer_data
		##print("key detected")
	if (int_buffer_prefix == status_key):
		##print("status detected")
		st=int_buffer_data
		horizon_state=0
	if (int_buffer_prefix == cal_key):
		cal=int_buffer_data
		##print("cal detected")
	if (int_buffer_prefix == h_key):
		h= int_buffer_data/16
		##print("heading detected")
	if (int_buffer_prefix == r_key):
		r=(int_buffer_data-offset)/(0x10)
		##print("roll detected")
	if (int_buffer_prefix == p_key):
		p=(int_buffer_data-offset)/(0x10)
		##print("pitch detected")
		
#Only update globals after key is verified
	# if (key==0xabcd):
	# 	##print("VERIFIED")
	# 	heading = h
	# 	roll = r
	# 	pitch = p
	# 	calibration=cal
	# 	status=st
	# 	delimiter=':|:'
	# 	logline=delimiter+str(h)+delimiter+str(r)+delimiter+str(p)+delimiter+str(hex(cal))+delimiter+str(hex(st))
	# 	# video_overlay()
	# 	#reset verifications for next loop
	# 	##print ("cal:" + str(cal) + " heading:"+str(h)+" roll:"+str(r)+" pitch:"+str(p))
	# 	log.info(logline)
	# 	key=0x0
	if  (status & 0x0800) == 0x0800:
		shutdownPi()
	# time.sleep(0.0002)
	return_dict = {
		'heading':heading,
		'roll':roll,
		'pitch':pitch,
		'calibration':calibration,
		'status':status
	}
	return return_dict

	
	




