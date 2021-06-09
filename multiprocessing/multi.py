# Patrick McCorkell
# April 2021
# US Naval Academy
# Robotics and Control TSD
#

from threading import Thread
from multiprocessing import Process, Pipe
import surface
import xb
import mbed_wrapper
# import plotting
from time import sleep, time, monotonic
import atexit
from gc import collect as trash
import mocap
import surface
from json import dumps,loads

daemon_mode = True


max_speed = 400   # us		speed limit
rigid_body_name = 'RedDwarf'
# qtm_server='192.168.5.4'   # IP of PC running QTM Motive
qtm_server = '192.168.42.24'

pwm_interval = 0.02		# seconds
qtm_interval = 0.005	# seconds
xbox_interval = 0.10	# seconds
mbed_interval = 0.02	# seconds
plot_interval = .1		# seconds


####################################
# Event Flags for Thread signalling.
####################################
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



#########################################################################
###################### PCA9685 PWM and ESC Section ######################
#########################################################################
#########################################################################

measured_active = {
	'heading' : 0xffff
}

def pwm_setup():
	global vessel
	vessel = surface.Controller()
	vessel.stopAll()
	vessel.thrusters.servoboard.set_max(max_speed/1.2)

def pwm_controller_thread():
	global vessel
	interval = pwm_interval
	while(pwm_flag.set_flag()):
		start=monotonic()+interval
		# vessel.surfaceLoop()
		vessel.azThrusterLogic()
		sleep(max(start-monotonic(),0))



##################################################################################
###################### Xbox 360 Wireless Controller Section ######################
##################################################################################
##################################################################################

def xbox_process_setup():
	global daemon_mode
	global xb_pipe_in,xb_pipe_out,xbox_process,xbox_controller
	xb_pipe_in, xb_pipe_out = Pipe()
	try:
		xbox_controller = xb.XBoxController(xb_pipe_in)
	except IOError as e:
		exit_program()
		print(e)
		quit()
	xbox_controller.max_speed = max_speed
	xbox_process = Process(target=xbox_controller.stream,daemon=daemon_mode)
	xbox_process.start()


# Debouncing for xbox toggle switches.
# debounce_timer stores last time updated.
# debounce_time_check is the time, in seconds, to debounce.
# val1 shall be the current value.
# val2 shall be the updating value from xbox controller.
debounce_timer = monotonic()
debounce_time_check = 1.0
def xbox_debounce(val1,val2):
	global debounce_timer, debounce_time_check
	current = monotonic()

	# if (bool_val):
	# 	returnval = val1 ^ val2
		# if returnval != val1:
			# debounce_timer = monotonic()
	# else:
	# 	returnval = val1
	bool_val = bool(max(current-debounce_timer-debounce_time_check,0))
	returnval = (bool_val * (val1 ^ val2)) + ((not bool_val) * val1)
	not_timer_bool = (returnval ^ val1)
	debounce_timer = (monotonic() * (not_timer_bool)) + (debounce_timer * (not not_timer_bool))

	return returnval

xbox = {
	'facing':999,
	'offset':999,
	'speed':999,
	'maintain':1,
	'mode':1,		# mode 1 qtm, mode 0 bno
	'quit':0
}
def xbox_read():
	global xb_pipe_out, xbox
	global vessel, qtm, bno, measured_active
	read_pipe = xb_pipe_out
	buffer = {}
	while (read_pipe.poll()):
		buffer = read_pipe.recv()
	if buffer:
		# print('xbox_read: '+str(buffer))

		vessel.persistent_offset = buffer['offset']

		# if (xbox['maintain']==1):
		# 	vessel.issueCommand('hea',xbox['facing'])
		# else:
		# 	vessel.issueCommand('hea',999)
		vessel.persistent_heading = bool(buffer['maintain']) and buffer['facing']

		# if (xbox['speed']>10):
		# 	vessel.issueCommand('vel',xbox['speed'])
		# else:
		# 	vessel.issueCommand('vel',999)
		vessel.persistent_speed = bool(max(buffer['speed']-10,0)) * buffer['speed']

		buffer['maintain'] = xbox_debounce(xbox['maintain'],buffer['maintain'])
		buffer['mode'] = xbox_debounce(xbox['mode'],buffer['mode'])

		for k in measured_active:
			measured_active[k] = (buffer['mode'] * qtm[k]) + ((not buffer['mode']) * bno[k])

		xbox = buffer

def xbox_stream():
	global xbox, measured_active, xbox_interval, xbox_flag
	interval = xbox_interval
	while(xbox_flag.set_flag()):
		start = monotonic()+interval
		xbox_read()
		sleep(max(start-monotonic(),0))
		# print(xbox)



#########################################################################
###################### BNO on MBED LPC1768 Section ######################
#########################################################################
#########################################################################

def mbed_process_setup():
	global mbed_pipe_in,mbed_pipe_out,mbed_process,imu,mbed_process
	mbed_pipe_in,mbed_pipe_out = Pipe()
	imu = mbed_wrapper.BNO(mbed_pipe_in)
	mbed_process = Process(target=imu.stream,daemon=daemon_mode)
	mbed_process.start()

bno = {
	'heading':999,
	'roll':999,
	'pitch':999,
	'calibration':999,
	'status':999
}
def mbed_read():
	global mbed_pipe_out, bno
	read_pipe = mbed_pipe_out
	buffer = {}
	while (read_pipe.poll()):
		buffer = read_pipe.recv()
	if buffer:
		bno = buffer

def mbed_stream():
	global mbed_interval, mbed_flag
	interval = mbed_interval
	while(mbed_flag.set_flag()):
		start = monotonic()+interval
		mbed_read()
		sleep(max(start-monotonic(),0))
		# print('bno: '+str(bno))




##############################################################
###################### Qualisys Section ######################
##############################################################
##############################################################

def qtm_process_setup():
	global qualisys, qtm_server,qtm_pipe_out,qtm_process
	qtm_pipe_in, qtm_pipe_out = Pipe()
	qualisys = mocap.Motion_Capture(qtm_pipe_in,qtm_server)

	# executor = concurrent.futures.ProcessPoolExecutor(max_workers=2)
	qtm_process = Process(target=qualisys.start,daemon=daemon_mode)
	qtm_process.start()

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
	global qtm_pipe_out, qtm
	read_pipe = qtm_pipe_out
	buffer = {}
	while (read_pipe.poll()):
		buffer = read_pipe.recv().get(name)
	if buffer:
		qtm = buffer
def qtm_stream():
	global qtm, qtm_flag, rigid_body_name
	interval = qtm_interval
	r_name = rigid_body_name
	while(qtm_flag.set_flag()):
		start=monotonic()+interval
		qtm_read(r_name)
		sleep(max(start-monotonic(),0))
		# print(qtm)




##############################################################
###################### Plotting Section ######################
##############################################################
##############################################################

def plot_process_setup():
	global plot_pipe_out,plot_process
	plot_pipe_in,plot_pipe_out = Pipe()
	plot_live = plotting.Plotting(plot_pipe_in)
	plot_process = Process(target=plot_live.start_display,daemon=daemon_mode)
	plot_process.start()

def plot_send_data():
	global qtm,bno,plot_pipe_out
	output = {
		'bno':bno,
		'qtm':qtm
	}
	plot_pipe_out.send(output)

def plot_stream():
	global plot_flag, plot_interval
	interval = plot_interval
	while(plot_flag.set_flag()):
		start=monotonic()+interval
		plot_send_data()
		sleep(max(start-monotonic(),0))



##################################################################
###################### Exit Program Section ######################
##################################################################
##################################################################

def exit_program():
	global pwm_flag,qtm_flag,xbox_flag,mbed_flag,plot_flag
	global xbox_process,mbed_process,qtm_process
	global qualisys,imu,xb_controller,vessel
	print("Shutting down threads.")
	pwm_flag.set_flag(0)
	qtm_flag.set_flag(0)
	xbox_flag.set_flag(0)
	mbed_flag.set_flag(0)
	plot_flag.set_flag(0)
	print()

	for i in range(1,4):
		vessel.thrusters.exitProgram()
		print(f'STOPPING THRUSTERS: {i}')
	print()

	print("Killing child processes.")
	try:
		xbox_process.kill()
	except Exception as e:
		print(e)
	try:
		mbed_process.kill()
	except Exception as e:
		print(e)
	try:
		qtm_process.kill()
	except Exception as e:
		print(e)
	try:
		plot_process.kill()
	except Exception as e:
		print(e)
	print()

	print('Disconnecting QTM connection.')
	try:
		qualisys.connected.disconnect()
	except Exception as e:
		print(e)

	print('Closing xbox controller.')
	try:
		xb_controller.close()
	except Exception as e:
		print(e)

	print('Shutting down mbed Serial.')
	try:
		imu.close()
	except Exception as e:
		print(e)

	print("Shutting down plotting function.")
	try:
		plot_live.close()
	except Exception as e:
		print(e)

	# print('Shutting down graphs.')

	print()
	print('Exiting Program.')
	print()


atexit.register(exit_program)



##################################################################
###################### Main Program Section ######################
##################################################################
##################################################################

def setup():
	global daemon_mode

	pwm_setup()
	pwm_thread = Thread(target=pwm_controller_thread,daemon=daemon_mode)
	pwm_thread.start()

	qtm_process_setup()
	qtm_thread = Thread(target=qtm_stream,daemon=daemon_mode)
	qtm_thread.start()

	mbed_process_setup()
	mbed_thread = Thread(target=mbed_stream,daemon=daemon_mode)
	mbed_thread.start()

	xbox_process_setup()
	xbox_thread = Thread(target=xbox_stream,daemon=daemon_mode)
	xbox_thread.start()

	# plot_process_setup
	# plot_thread = Thread(target=plot_stream,daemon=daemon_mode)
	# plot_thread.start()

def loop():
	while(not xbox['quit']):
		# xbox_read()
		# mbed_read()
		# qtm_read(rigid_body_name)

		# print('MAIN xbx: '+dumps(xbox))
		# print('MAIN qtm: '+dumps(qtm))
		# print('MAIN bno: '+dumps(bno))
		print()
		print('MAIN use: '+dumps(measured_active))
		# print('vessel: '+ str(vessel.thrusters))
		print()
		sleep(0.1)
		trash()
	exit_program()

setup()
loop()