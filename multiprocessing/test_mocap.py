import mocap
from threading import Thread
from time import sleep
from multiprocessing import Process, Pipe

qtm_server='192.168.5.4'
qtm={}

def qtm_setup():
	global qualisys, qtm_server,qtm_pipe_in
	qtm_pipe_in, qtm_pipe_out = Pipe()
	qualisys = mocap.Motion_Capture(qtm_pipe_out,qtm_server)

	mocap_process = Process(target=qualisys.start,daemon=True)
	mocap_process.start()

# avg of 50us in this function when sampled at 10ms, 20ms, and 50ms intervals, over 1000 iterations each time.
# def read_qtm(read_pipe=qtm_pipe_in):
def read_qtm():
	read_pipe = qtm_pipe_in
	buffer = {}
	while (read_pipe.poll()):
		buffer = read_pipe.recv()
	# print(buffer)
	return buffer

qtm= {}
def stream_qtm():
	global qtm
	while(1):
		placeholder = read_qtm()
		if placeholder:
			qtm = placeholder
		#print(qtm)


qtm_setup()
my_thread = Thread(target=stream_qtm)

def main():
	global qtm
	while(1):
		print(qtm)
		sleep(1)

if __name__ == '__main__':
	my_thread.start()
	main()