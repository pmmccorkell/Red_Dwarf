# Patrick McCorkell
# April 2021
# US Naval Academy
# Robotics and Control TSD
#


import mocap
from threading import Thread
from time import sleep, time
from multiprocessing import Process, Pipe

qtm_server='192.168.5.4'
qtm={}
rigid_body_name='RedDwarf'

def qtm_setup():
	global qtm_server,qtm_pipe_in
	qtm_pipe_in, qtm_pipe_out = Pipe()
	qualisys = mocap.Motion_Capture(qtm_pipe_out,qtm_server)

	mocap_process = Process(target=qualisys.start,daemon=True)
	mocap_process.start()


# avg of 50us in this function when sampled at 10ms, 20ms, and 50ms intervals, over 1000 iterations each time.
# def read_qtm(read_pipe=qtm_pipe_in):
def qtm_read(name):
	global qtm_pipe_in, qtm
	read_pipe = qtm_pipe_in
	# name = rigid_body_name
	buffer = {}
	while (read_pipe.poll()):
		buffer = read_pipe.recv().get(name)
	if buffer:
		qtm = buffer

def qtm_stream():
	global qtm,rigid_body_name
	interval = 0.005
	while(1):
		start = time()
		qtm_read(rigid_body_name)
		diff = interval+start-time()
		sleeptime = max(diff,0)
		sleep(sleeptime)
		# print('index: '+str(qtm['index']) + ', time: '+str(sleeptime))


qtm_setup()
my_thread = Thread(target=qtm_stream)

def main():
	global qtm
	while(1):
		print(qtm)
		sleep(1)

from timeit import timeit
def timingtest(wait_time=0.01):
	sample = []
	for _ in range(1000):
		sample.append(timeit(stmt=read_qtm,number=1000))
		sleep(wait_time)
	return sample


if __name__ == '__main__':
	my_thread.start()
	main()