from threading import Thread
from time import sleep, monotonic
# import pandas as pd
from matplotlib import pyplot as plt
from matplotlib import animation, style
import numpy as np
from random import randint
from multiprocessing import Process, Pipe
from gc import collect as trash
import os

measured_active = {
	'heading' : 45
}

xbox = {
	'facing':181,
	'offset':182,
	'speed':183,
	'maintain':1,
	'mode':11,		# mode 1 qtm, mode 0 bno
	'quit':0
}

bno = {
	'heading':271,
	'roll':272,
	'pitch':273,
	'calibration':0x33,
	'status':0xff
}

qtm = {
			'index':1000,
			'x':51,
			'y':52,
			'z':53,
			'roll':291,
			'pitch':292,
			'heading':293
}

pwm = {
	'forePort':300,
	'foreStar':301,
	'aftPort':302,
	'aftStar':303
}


def plotting():
	
	hea_plot = pd.DataFrame.from_dict(a_data_frame['x_axis'])
	hea_plot.plot()

	# data_frames = read_csv()

	# Iterate through the list[] of Data Frames.
	# for data_frame in data_frames:
		# Plot each Data Frame separately. Assigning the x-axis and y-axis as it is on the Oscope.
		# data_frame.plot(x='time',y='voltage')

	# plt.show()



def setup():
	plot_thread = Thread(target=plotting,daemon=True)
	#plot_thread.start()


def update_data():
	global bno,qtm,start,plot_pipe_out
	print("start update thread")
	while(1):
		for _ in range(1000):
			bno['heading']+=1
			qtm['heading']-=1
			output = {
				'bno':bno,
				'qtm':qtm
			}
			plot_pipe_out.send(output)
			sleep(0.01)
		for _ in range(1000):
			bno['heading']-=1
			qtm['heading']+=1
			output = {
				'bno':bno,
				'qtm':qtm
			}
			plot_pipe_out.send(output)
			sleep(0.01)
		print("update thread cycle: " +str(monotonic()-start_time))

start_time = monotonic()

def test():
	global bno,qtm,start_time
	plt.ion()
	fig = plt.figure(figsize=(16,16))
	axes = fig.add_subplot(111)	#add 1 subplot of 1 figure in 1 plot
	axes.set_ylim(-1000,2000)
	axes.set_xlim(0,11)

	# start_time = monotonic()
	data_plot=plt.plot(0,0)
	line1, = axes.plot([],[],lw=2,color='b',label='bno')
	line2, = axes.plot([],[],lw=2,color='r',label='qtm')
	axes.legend()
	x,y1,y2=[],[],[]
	plt.title('qtm vs bno heading')
	for i in range(100):
		x.append(monotonic() - start_time)
		y1.append(bno['heading'])
		y2.append(qtm['heading'])
		line1.set_ydata(y)
		line1.set_xdata(x)
		line2.set_ydata(y2)
		line2.set_xdata(x)
		# if len(y)>0:
		# 	axes.set_ylim(min([min(y1),min(y2)]),max([max(y1),max(y2)])+1) # +1 to avoid singular transformation warning
		# 	axes.set_xlim(min(x),max(x)+1)
		# plt.title('qtm vs bno: '+str(i))
		plt.draw()
		plt.pause(0.0000001)

	print('test stop: '+str(monotonic()-start_time))
	plt.show(block=True)



def np_test():
	global bno,qtm,start_time
	plt.ion()
	fig = plt.figure(figsize=(16,16))
	axes = fig.add_subplot(111)	#add 1 subplot of 1 figure in 1 plot
	axes.set_ylim(-1000,2000)
	axes.set_xlim(0,11)

	# start_time = monotonic()
	data_plot=plt.plot(0,0)
	line1, = axes.plot([],[],lw=2,color='b',label='bno')
	line2, = axes.plot([],[],lw=2,color='r',label='qtm')
	axes.legend()
	x=np.array(monotonic()-start_time)
	y1=np.array(bno['heading'])
	y2=np.array(qtm['heading'])
	plt.title('qtm vs bno heading')
	for i in range(100):
		x = np.append(x,monotonic() - start_time)
		y1 = np.append(y1,bno['heading'])
		y2 = np.append(y2,qtm['heading'])
		line1.set_ydata(y1)
		line1.set_xdata(x)
		line2.set_ydata(y2)
		line2.set_xdata(x)
		# if len(y)>0:
		# 	axes.set_ylim(min([min(y),min(y2)]),max([max(y),max(y2)])+1) # +1 to avoid singular transformation warning
		# 	axes.set_xlim(min(x),max(x)+1)
		# plt.title('qtm vs bno: '+str(i))
		plt.draw()
		plt.pause(0.0000001)

	print('test stop: '+str(monotonic()-start_time))
	plt.show(block=True)

class Plotting:
	def __init__(self,communicator):
		self.run = 1
		self.comms=communicator
		self.start_time = monotonic()
		self.bno={
			'heading':50
		}
		self.qtm={
			'heading':10
		}

	def close(self):
		self.run = 0

	def read_in_data(self):
		buffer = None
		while(self.comms.poll()):
			buffer = self.comms.recv()
		if (buffer):
			self.bno = buffer['bno']
			self.qtm = buffer['qtm']

	def run_animation(self):
		style.use('fivethirtyeight')
		fig = plt.figure()
		self.ax1 = fig.add_subplot(1,1,1)

		self.x = [0.0]*100
		self.y1 = [0.0]*100
		self.y2 = [0.0]*100

		# Heading for the plot.
		plt.title('qtm vs bno heading')

		# Do not change #s on axis to scientific notation.
		plt.ticklabel_format(style='plain')

		self.start_time=monotonic()
		ani = animation.FuncAnimation(fig,self.animate,interval=1000)
		plt.show()

	def animate(self,i):
		# graph_data = open('example.txt','r').read()
		# lines = graph_data.split('\n')
		self.read_in_data()
		self.x.pop(0)
		self.y1.pop(0)
		self.y2.pop(0)

		current_time=round(monotonic()-self.start_time,2)
		self.x.append(current_time)
		self.y1.append(self.bno['heading'])
		self.y2.append(self.qtm['heading'])

		line1.set_ydata(y1)
		line1.set_xdata(x)
		line2.set_ydata(y2)
		line2.set_xdata(x)

		self.ax1.clear()
		self.ax1.plot(self.x, self.y1)
		self.ax1.plot(self.x, self.y2)
		

	def last_test(self):
		# global bno,qtm,start_time
		set_core_affinity(0)
		plt.ion()
		fig = plt.figure(figsize=(16,16))
		axes = fig.add_subplot(111)	#add 1 subplot of 1 figure in 1 plot
		axes.set_ylim(0,10)
		axes.set_xlim(0,11)

		self.start_time = monotonic()
		data_plot=plt.plot(0,0)
		line1, = axes.plot([],[],lw=2,color='b',label='bno')
		line2, = axes.plot([],[],lw=2,color='r',label='qtm')

		# Display the labels.
		axes.legend()

		# Initialize x and y axis variables.
		x,y1,y2=[0.0]*100,[0.0]*100,[0.0]*100

		# Heading for the plot.
		plt.title('qtm vs bno heading')

		# Do not change #s on axis to scientific notation.
		plt.ticklabel_format(style='plain')

		while(1):
			self.read_in_data()
			x.pop(0)
			y1.pop(0)
			y2.pop(0)

			current_time=round(monotonic()-self.start_time,2)
			x.append(current_time)
			y1.append(self.bno['heading'])
			y2.append(self.qtm['heading'])

			line1.set_ydata(y1)
			line1.set_xdata(x)
			line2.set_ydata(y2)
			line2.set_xdata(x)

			axes.set_ylim(min([min(y1),min(y2)]),max([max(y1),max(y2)])+1) # +1 to avoid singular transformation warning
			axes.set_xlim(min(x),max(x)+1)
			plt.draw()
			plt.pause(0.0000001)

		print('test stop: '+str(monotonic()-self.start_time))
		plt.show(block=True)

def set_core_affinity(x=0):
	cores = os.cpu_count() - 1
	my_pid = os.getpid()
	chosen_core = {max(cores-x,0)}
	os.sched_setaffinity(my_pid,chosen_core)

def plot_process_setup():
	global plot_pipe_in,plot_pipe_out,plot_process
	set_core_affinity(1)
	plot_pipe_in,plot_pipe_out = Pipe()
	plotting = Plotting(plot_pipe_in)
	# plot_process = Process(target=plotting.last_test,daemon=True)
	plot_process = Process(target=plotting.run_animation)
	plot_process.start()


if __name__ == "__main__":
	print("running as main")
	plot_process_setup()
	sleep(1)
	data_thread = Thread(target=update_data,daemon=True)
	data_thread.start()

	while(1):
		sleep(1)
		trash()

