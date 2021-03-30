import surface
import xb
import atexit
from time import sleep, time
from threading import Thread
import multiprocessing

class event_flags:
	def __init__(self):
		self.value(1)

	def value(self,val=None):
		if val is not None:
			self.run_flag = val
		return self.run_flag

run_flag = event_flags()

def exit_program():
	print("exiting program")
	run_flag.value(0)
	xb.thrusters.exitProgram()
	#xb_process.terminate()
	#controller_process.terminate()
	#xb_process.join()
	#controller_process.join()

#atexit.register(exit_program)


xb_process = multiprocessing.Process(target=xb.run)
controller_process = multiprocessing.Process(target=xb.threadedController)


def xb_wrapper():
	global xp_process
	interval_timer = 0.05
	while(run_flag.value()):
		time_0 = time()
		xb_process = multiprocessing.Process(target=xb.run)
		xb_process.start()
		xb_process.join()

		diff = time() - time_0
		sleeptime = max(interval_timer - diff,0.0)
		sleep(sleeptime)

	xb_process.terminate()
	xb_process.join()


def controller_wrapper():
	global controller_process
	interval_timer = 0.02
	
	while(run_flag.value()):
		time_0 = time()
		controller_process = multiprocessing.Process(target=xb.azThrusterLogic)
		controller_process.start()
		controller_process.join()

		diff = time() - time_0
		sleeptime = max(interval_timer - diff,0.0)
		sleep(sleeptime)
	controller_process.terminate()
	controller_process.join()

if __name__ == '__main__':
	xb_thread = Thread(target=xb_wrapper,daemon=True)
	controller_thread = Thread(target=controller_wrapper,daemon=True)
	xb_thread.start()
	controller_thread.start()
	while(1):
		sleep(1)
