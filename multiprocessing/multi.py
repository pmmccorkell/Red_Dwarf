import concurrent.futures
from threading import Thread
import surface
import xb
import mbed
from time import sleep, time
import atexit
import gc

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
def pwm_controller( ... ARGS ...):
	global pwm
	interval = 0.02
	for k in measured_active:
		measured_active[k] = (qtm[k] * xbox['mode']) + (bno[k] * (not xbox['mode']))
	# print(measured_active)
	executor = concurrent.futures.ProcessPoolExecutor(max_workers=3)
	while(pwm_flag.set_flag()):
		start = time()

		############ COME BACK TO THIS ONE ############
		pwm_process = executor.submit(surface. ????, measured_active)
		surface.azThrusterLogic()
		###############################################

		pwm = pwm_process.result()
		sleeptime = max(interval + start - time(), 0.0)
		sleep(sleeptime)
	print("shutting down executor")
	executor.shutdown(wait=False,cancel_futures=True)


qtm = {
	'heading' : 999,
	'roll' : 999,
	'pitch' : 999,
}
def qtm_process_thread():
	global qtm
	interval = 0.008
	executor = concurrent.futures.ProcessPoolExecutor(max_workers=3)
	while(qtm_flag.set_flag()):

		##################################################################
		qtm_process = executor.submit(qtm. ############# WRITE THIS #######)
		qtm = qtm_process.result()

		sleeptime  = max(interval + start - time(), 0.0)
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
	executor = concurrent.futures.ProcessPoolExecutor(max_workers=3)
	while(xbox_flag.set_flag()):
		start = time()
		incoming_commands = {}

		xbox_process = executor.submit(mbed.get_angles)
		xbox = xbox_process.result()

		xbox_flag.set_flag(xbox['quit'])

		def process_commands():
			for k,v in incoming_commands:
				surface.issueCommand(k,v)
				return surface.thrusters.update()

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
	executor = concurrent.futures.ProcessPoolExecutor(max_workers=3)
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
	while(plot_flag.set_flag()):
		start = time()

		############ GRAPH AND COMPARE THINGS ############


		sleeptime = max(interval + start - time(), 0.0)
	

############## SEE THREAD PATTERN ###########
pwm_thread = Thread(target=pwm_process_thread,daemon=True)
pwm_thread.start()

qtm_thread = Thread(target=qtm_process_thread,daemon=True)
qtm_thread.start()

xbox_thread = Thread(target=xbox_process_thread,daemon=True)
xbox_thread.start()

mbed_thread = Thread(target=mbed_process_thread,daemon=True)
mbed_thread.start()

plot_thread = Thread(target=plotting,daemon=True)
plot_thread.start()


def exit_program():
	print("exiting program")
	pwm_flag.set_flag(0)
	pwm_flag.set_flag(0)
	pwm_flag.set_flag(0)
	pwm_flag.set_flag(0)
	pwm_flag.set_flag(0)

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


#######################################################

############### CHECK THESE #####################

#############################################################

max_speed = 400
maintain_facing = 1

in main:
	qtm.mqtt_connect()

	maximum = max_speed / 1.2
	fail=0
	thrusters.servoboard.set_max(maximum)

	check_maintain()

			if (maintain_facing==1):
				issueCommand('hea',f)
			else:
				issueCommand('hea',999)

			if (o==0):
				o=999
			issueCommand('off',o)

			if (s<10):
				s=999
			issueCommand('vel',s)

		surfaceLoop()
		# azThrusterLogic()
		sleep(0.05)






