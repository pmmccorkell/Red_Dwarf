from pyqtgraph.Qt import QtGui, QtCore
# import numpy as np
import pyqtgraph as pg
from time import monotonic,sleep
from gc import collect as trash
from threading import Thread


class Plotting:
	def __init__(self,communictor,timing_val=20):
		self.display_graph_timer=timing_val
		self.comms = communictor
		self.exit_state = 0


	def start_display(self):
		self.app = pg.mkQApp("Plotting Example")

		self.win = pg.GraphicsLayoutWidget(show=True, title="Basic plotting example")
		self.win.resize(1000,600)
		self.win.setWindowTitle('pyqtgraph example: bno vs qtm')

		pg.setConfigOptions(antialias=True)


		self.p1 = win.addPlot(title="Updating plot")


		self.start_time = monotonic()



		self.p1.enableAutoRange(axis='x',enable=True)
		self.p1.enableAutoRange(axis='y',enable=False)
		self.p1.setYRange(-10,370)
		self.p1.addLegend()
		curve1 = p6.plot(pen='r',name='qtm')
		curve2 = p6.plot(pen='b',name='bno')
		self.p1.setLabel('left',"Heading (degrees)")
		self.p1.setLabel('bottom',"Time (seconds)")

		self.curve1 = self.p1.plot(pen='r')
		self.curve2 = self.p1.plot(pen='b')
		# data = np.random.normal(size=(10,1000))
		self.x_val,self.y1_val,self.y2_val = [0.0]*1000,[0.0]*1000,[0.0]*1000

		self.timer = QtCore.QTimer()
		self.timer.timeout.connect(self.update)
		self.timer.start(self.display_graph_timer)
		self.mkQApp().exec_()

	def read_in_data(self):
		while(1):
			buffer = None
			while(self.comms.poll()):
				buffer = self.comms.recv()
			if (buffer):
				self.bno = buffer['bno']
				self.qtm = buffer['qtm']
		
		sleep(0.01)
	
	def form_data(self):
		self.x_val.pop(0)
		self.y1_val.pop(0)
		self.y2_val.pop(0)

		self.x_val.append(monotonic()-self.start_time)
		self.y1_val.append(self.qtm['heading'])
		self.y2_val.append(self.bno['heading'])


	def update(self):
		self.curve1.setData(self.x_val,self.y1_val)
		self.curve2.setData(self.x_val,self.y2_val)







###############################################################
###################### Debugging Section ######################
###############################################################
###############################################################






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
			# plot_pipe_out.send(output)
			sleep(0.01)
		for _ in range(1000):
			bno['heading']-=1
			qtm['heading']+=1
			output = {
				'bno':bno,
				'qtm':qtm
			}
			# plot_pipe_out.send(output)
			sleep(0.01)
		# print("update thread cycle: " +str(monotonic()-start_time))


def form_data():
	while(1):
		for i in range(1000):
			x_val.pop(0)
			y1_val.pop(0)
			y2_val.pop(0)
			x_val.append(monotonic()-start_time)
			y1_val.append(bno['heading'])
			y2_val.append(qtm['heading'])
			sleep(0.001)


if __name__ == '__main__':
	data_thread = Thread(target=update_data,daemon=True)
	data_thread.start()

	array_thread = Thread(target=form_data,daemon=True)
	array_thread.start()

	timer = QtCore.QTimer()
	timer.timeout.connect(update)
	timer.start(20)	# ms

	pg.mkQApp().exec_()

	while(1):
		sleep(1)
		trash()
