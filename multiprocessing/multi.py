# Patrick McCorkell
# April 2021
# US Naval Academy
# Robotics and Control TSD
#

# import concurrent.futures
from threading import Thread
from multiporcessing import Process, Pipe
import surface
import xb
import mbed
from time import sleep, time
import atexit
from gc import trash
import mocap
import surface

qtm_server='192.168.5.4'   # IP of PC running QTM Motive

max_speed = 400   # us		speed limit

rigid_body_name = 'RedDwarf'

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

pwm_interval = 0.02		# 20 ms
qtm_interval = 0.005	# 5 ms
xbox_interval = 0.01	# 10 ms
mbed_interval = 0.02	# 20 ms
plot_interval = .1		# 100 ms

measured_active = {
	'heading' : 0xffff
}



def pwm_setup():
	vessel = surface.Controller()
	vessel.stopAll()

def pwm_controller_thread():
	interval = pwm_interval
	while(pwm_flag.set_flag()):
		start=time()
		vessel.azThrusterLogic()
		diff = (interval + start - time())
		sleeptime=max(diff,0)
		sleep(sleeptime)

def pwm_commands_thread():
	global xbox
	interval = pwm_interval*2
	while(pwm_flag.set_flag()):
		start=time()
		vessel.surfaceLoop()
		diff


###############################################################
#################################################################

############ COME BACK TO THIS ONE ############
# pwm = {
# 	##### Thruster Values ?? ####
# }
# def pwm_setup():
# 	global pwm_pipe_in
# 	pwm_pipe_in,pwm_pipe_out = Pipe()
# 	pwm_process = surface #. #####################
# 	##############################################
# 	##############################################
# 	##############################################







def xbox_process_setup():
	global xb_pipe_in,xbox_process,xbox_controller
	xb_pipe_in, xb_pipe_out = Pipe()
	xbox_controller = xb.XBoxController(xb_pipe_in)
	xbox_process = Process(target=xbox_controller.poll,daemon=True)
	xbox_process.start()

xbox = {
	'facing':999,
	'offset':999,
	'speed':999,
	'maintain':1,
	'mode':1,		# mode 1 qtm, mode 0 bno
	'quit':0
}
def xbox_read():
	global xbox_pipe_in, xbox
	read_pipe = xbox_pipe_in
	buffer = {}
	while (read_pipe.poll()):
		buffer = read_pipe.recv()
	if buffer:
		xbox = buffer
def xbox_stream():
	global xbox, measured_active, xbox_interval, xbox_flag
	interval = xbox_interval
	while(xbox_flag.set_flag()):
		start = time()
		xbox_read()
		for k in measured_active:
			measured_active[k] = (xbox['mode'] * qtm[k]) + ((not xbox['mode']) * bno[k])
		diff = interval+start-time()
		sleeptime=max(diff,0)
		sleep(sleeptime)
		# print('xbox: '+str(xbox))


def mbed_process_setup():
	global mbed_pipe_in,mbed_process,imu
	mbed_pipe_in,mbed_pipe_out = Pipe()
	imu = mbed_wrapper.BNO(mbed_pipe_in)
	mbed_process = Process(target=imu.stream,daemon=True)
	mbed_process.start()

bno = {
	'heading':999,
	'roll':999,
	'pitch':999,
	'calibration':999,
	'status':999
}
def mbed_read():
	global mbed_pipe_in, bno
	read_pipe = mbed_pipe_in
	buffer = {}
	while (read_pipe.poll()):
		buffer = read_pipe.recv()
	if buffer:
		bno = buffer
def mbed_stream():
	global mbed_interval, mbed_flag
	interval = mbed_interval
	while(mbed_flag.set_flag()):
		start = time()
		mbed_read()
		diff = interval+start-time()
		sleeptime=max(diff,0)
		sleep(sleeptime)
		# print('bno: '+str(bno))


def qtm_process_setup():
	global qualisys, qtm_server,qtm_pipe_in,mocap_process
	qtm_pipe_in, qtm_pipe_out = Pipe()
	qualisys = mocap.Motion_Capture(qtm_pipe_out,qtm_server)

	# executor = concurrent.futures.ProcessPoolExecutor(max_workers=2)
	mocap_process = Process(target=qualisys.start,daemon=True)
	mocap_process.start()

qtm = {
			'index':0xffff,
			'x':999,
			'y':999,
			'z':999,
			'roll':999,
			'pitch':999,
			'heading':999
}
def qtm_read(name):
	global qtm_pipe_in, qtm
	read_pipe = qtm_pipe_in
	# name = rigid_body_name
	buffer = {}
	while (read_pipe.poll()):
		buffer = read_pipe.recv().get(rigid_body_name)
	if buffer:
		qtm = buffer
def qtm_stream():
	global qtm, qtm_flag, rigid_body_name
	interval = 0.005
	r_name = rigid_body_name
	while(qtm_flag.set_flag()):
		start=time()
		qtm_read(r_name)
		diff = interval+start-time()
		sleeptime = max(diff, 0)
		sleep(sleeptime)
		# print(qtm)


def plotting():
	global bno,qtm,xbox,pwm,plotting_interval
	interval = plotting_interval
	while(plot_flag.set_flag()):
		start = time()

		############ GRAPH AND COMPARE THINGS ############


		sleeptime = max(interval + start - time(), 0.0)


def exit_program():
	global qualisys,imu,xb_controller
	print("Shutting down threads.")
	pwm_flag.set_flag(0)
	qtm_flag.set_flag(0)
	xbox_flag.set_flag(0)
	mbed_flag.set_flag(0)
	plot_flag.set_flag(0)
	print()

	for i in range(3):
		surface.thrusters.exitProgram()
		print(f'STOPPING THRUSTERS: {i}')
		sleep(0.3)
	print()

	print('Disconnecting QTM connection.')
	qualisys.connected.disconnect()

	print('Closing xbox controller.')
	xb_controller.close()

	print('Shutting down mbed Serial.')
	imu.close()

	# print('Shutting down graphs.')

	print()
	print('Exiting Program.')
	print()


atexit.register(exit_program)




def setup():
	surface.pwmControl.servoboard.set_max(max_speed/1.2)

	pwm_setup()
	pwm_thread = Thread(target=pwm_process_thread,daemon=True)
	pwm_thread.start()

	qtm_process_setup()
	qtm_thread = Thread(target=qtm_stream,daemon=True)
	qtm_thread.start()

	xbox_process_setup()
	xbox_thread = Thread(target=xbox_stream,daemon=True)
	xbox_thread.start()

	mbed_process_setup()
	mbed_thread = Thread(target=mbed_stream,daemon=True)
	mbed_thread.start()



	plot_thread = Thread(target=plotting,daemon=True)
	plot_thread.start()


setup()
