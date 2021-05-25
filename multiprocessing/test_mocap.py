import mocap
from threading import Thread
from time import sleep
import concurrent.futures
import asyncio
from multiprocessing import Process, Queue, Pipe

# a=mocap.Motion_Capture()

# def start_mocap():
	#1
	# asyncio.ensure_future(a.connect())	
	# asyncio.get_event_loop().run_forever()

	#2
	# some_future = asyncio.get_event_loop().create_future()
	# asyncio.get_event_loop().run_until_complete(some_future)

	#3
	# global some_await
	# some_await = asyncio.create_task(a.connect())


# async def main():
def main():
	# global some_await
	# mocap_thread = Thread(target=mocap.stream_data)
	# mocap_thread.start()
	# mocap_thread.start()

	# executor = concurrent.futures.ProcessPoolExecutor(max_workers=2)
	# mocap_process = executor.submit(a.start)
	# start_mocap()

	mocap.stream_data()


	print('got past asyncio')


	while(1):
		sleep(1)
		print('data: '+str(mocap.data_in))
	# await some_await


# main()
# asyncio.run(main())

qtm_server='192.168.5.4'
qtm={}

def qtm_setup():
	global qualisys, qtm_server,qtm_pipe_in
	qtm_pipe_in, qtm_pipe_out = Pipe()
	qualisys = mocap.Motion_Capture(qtm_pipe_out,qtm_server)

	# executor = concurrent.futures.ProcessPoolExecutor(max_workers=2)
	mocap_process = Process(target=qualisys.start,daemon=True)
	mocap_process.start()

# avg of 50us in this function when sampled at 10ms, 20ms, and 50ms intervals, over 1000 iterations each time.
def read_qtm(read_pipe=qtm_pipe_in):
	buffer = {}
	while (read_pipe.poll()):
		buffer = read_pipe.recv()
	return buffer

def stream_qtm():
	global qtm, qtm_pipe_in, qualisys
	mocap_process = Process(target=qualisys.start,daemon=True)
	mocap_process.start()

	while(1):
		sleep(0.0001)
		buffer = {}
		while (qtm_pipe_in.poll()):
			buffer = qtm_pipe_in.recv()
		if buffer:
			qtm = buffer
		print(qtm)

qtm_setup()
#stream_qtm()