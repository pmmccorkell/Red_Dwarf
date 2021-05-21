# Patrick McCorkell
# April 2021
# US Naval Academy
# Robotics and Control TSD
#

import concurrent.futures
from threading import Thread
import surface
import xb
import mbed
from time import sleep, time
import atexit
from gc import trash
import mocap

qtm_server='192.168.5.4'   # IP of PC running QTM Motive

max_speed = 400   # us		speed limit

rigid_body_name = 'RED Dwarf'

class event_flags:
	def __init__(self):
		self.set_flag(1)

	def set_flag(self,val=None):
		if val is not None:
			self.run_flag = val
		return self.run_flag

pwm_flag = event_flags()
qtm_flag = event_flags()
xbox_flag = event_flags()
mbed_flag = event_flags()
plot_flag = event_flags()

measured_active = {
	'heading' : 0xffff
}

###############################################################
#################################################################

############ COME BACK TO THIS ONE ############
pwm = {
	##### Thruster Values ?? ####
}
def pwm_process_thread( ... ARGS ...):
	global pwm
	interval = 0.02


	#############
	# This part better in xbox process ?
	#############
	# for k in measured_active:
	# 	measured_active[k] = (qtm[k] * xbox['mode']) + (bno[k] * (not xbox['mode']))
	# print(measured_active)


	executor = concurrent.futures.ProcessPoolExecutor(max_workers=2)
	while(pwm_flag.set_flag()):
		start = time()

		################# CHECK THIS ####################
		##################################
		##############################
		# def process_commands():
		for k,v in incoming_commands:
			surface.issueCommand(k,v)
			# return surface.thrusters.update()

		############ COME BACK TO THIS ONE ############
		pwm_process = executor.submit(surface. ????, measured_active)
		surface.azThrusterLogic()
		###############################################

		pwm = pwm_process.result()
		sleeptime = max(interval + start - time(), 0.0)
		sleep(sleeptime)
	print("shutting down executor")
	executor.shutdown(wait=False,cancel_futures=True)


xbox = {
	'facing':999,
	'offset':999,
	'speed':999,
	'maintain':1,
	'mode':1,		# mode 1 qtm, mode 0 bno
	'quit':0
}
def xbox_process_thread():
	global xbox
	interval = 0.01
	executor = concurrent.futures.ProcessPoolExecutor(max_workers=2)
	xbox_buffer = xbox
	while(xbox_flag.set_flag()):
		start = time()
		incoming_commands = {}

		xbox_process = executor.submit(mbed.get_angles)
		xbox_buffer = xbox_process.result()


		# if xbox_buffer['mode'] = 1, use QTM MoCap data for control
		# if xbox_buffer['mode'] = 0, use BNO-055 IMU data for control
		for k in measured_active:
			measured_active[k] = xbox_buffer['mode'] * qtm[k]) + (not xbox_buffer['mode']) * bno[k]


		# Quit if quit signal is sent
		xbox_flag.set_flag(xbox_buffer['quit'])

		xbox = xbox_buffer

		sleeptime  = max(interval + start - time(), 0.0)
		sleep(sleeptime)
	print("shutting down executor")
	executor.shutdown(wait=False,cancel_futures=True)
	exit_program()



bno = {
	'heading':999,
	'roll':999,
	'pitch':999,
	'calibration':999,
	'status':999
}
def mbed_process_thread():
	global bno
	interval = 0.03
	executor = concurrent.futures.ProcessPoolExecutor(max_workers=2)
	while(mbed_flag.set_flag()):
		start = time()
		mbed_process = executor.submit(mbed.get_angles)
		bno = mbed_process.result()
		sleeptime = max(interval + start - time(), 0.0)
		sleep(sleeptime)
	print("shutting down executor")
	executor.shutdown(wait=False,cancel_futures=True)



def plotting():
	global bno,qtm,xbox,pwm
	interval = 1.0
	while(plot_flag.set_flag()):
		start = time()

		############ GRAPH AND COMPARE THINGS ############


		sleeptime = max(interval + start - time(), 0.0)
	

def exit_program():
	global qtm
	print("exiting program")
	pwm_flag.set_flag(0)
	qtm_flag.set_flag(0)
	xbox_flag.set_flag(0)
	pwm_flag.set_flag(0)
	plot_flag.set_flag(0)

	qtm.connected.disconnect()

	print()
	print('Exiting Program.')
	print()

	xb.close()
	for i in range(3):
		surface.thrusters.exitProgram()
		print(f'STOPPING THRUSTERS: {i}')
		sleep(0.3)

	print()

atexit.register(exit_program)


def qtm_setup():
	global qtm, qtm_server
	qtm = mocap.Motion_Capture(qtm_server)
	# executor = concurrent.futures.ProcessPoolExecutor(max_workers=2)


def setup():
	surface.pwmControl.servoboard.set_max(max_speed/1.2)
	surface.stopAll()

	pwm_thread = Thread(target=pwm_process_thread,daemon=True)
	pwm_thread.start()

	qtm_setup() 
	# qtm_thread = Thread(target=qtm_process_thread,daemon=True)
	# qtm_thread.start()

	xbox_thread = Thread(target=xbox_process_thread,daemon=True)
	xbox_thread.start()

	mbed_thread = Thread(target=mbed_process_thread,daemon=True)
	mbed_thread.start()

	plot_thread = Thread(target=plotting,daemon=True)
	plot_thread.start()


setup()
