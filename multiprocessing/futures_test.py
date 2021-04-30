import concurrent.futures
from time import sleep, time
import atexit
from threading import Thread

whatwillitbe = 1

class event_flags:
	def __init__(self):
		self.set_flag(1)

	def set_flag(self,val=None):
		if val is not None:
			self.run_flag = val
		return self.run_flag


def test():
	sleep(0.004)
	return 999

test_flag = event_flags()

def test_process_thread():
	global whatwillitbe, test_process
	interval = 0.01
	executor = concurrent.futures.ProcessPoolExecutor(max_workers=3)
	while(test_flag.set_flag()):
		start = time()
		# with concurrent.futures.ProcessPoolExecutor() as executor:
		test_process = executor.submit(test)
		print('in process: ' + str(whatwillitbe))
		whatwillitbe = test_process.result()
		print('process finished: ' + str(whatwillitbe))
		sleeptime = max(interval + start - time(),0.0)
		sleep(sleeptime)
	print("shutting down executor")
	executor.shutdown(wait=False,cancel_futures=True)


test_thread = Thread(target=test_process_thread,daemon=True)
test_thread.start()

def exit_program():
	test_flag.set_flag(0)
	sleep(0.1)
	print()
	print()
	print("atexit triggered")
	sleep(0.5)
	print()
	print("Exiting program")
	sleep(0.5)
	print()
	print()

atexit.register(exit_program)

def main():
	global whatwillitbe
	while(1):
		whatwillitbe -= 9
		print('main: '+str(whatwillitbe))
		sleep(0.001)
	#exit_program()

main()