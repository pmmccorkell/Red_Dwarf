from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
from time import monotonic,sleep
from gc import collect as trash
from threading import Thread

app = pg.mkQApp("Plotting Example")
#mw = QtGui.QMainWindow()
#mw.resize(800,800)

win = pg.GraphicsLayoutWidget(show=True, title="Basic plotting example")
win.resize(1000,600)
win.setWindowTitle('pyqtgraph example: bno vs qtm')

# Enable antialiasing for prettier plots
pg.setConfigOptions(antialias=True)


p6 = win.addPlot(title="Updating plot")

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

start_time = monotonic()



p6.enableAutoRange(axis='x',enable=True)
p6.enableAutoRange(axis='y',enable=False)
p6.setYRange(-800,1200)

curve1 = p6.plot(pen='r')
curve2 = p6.plot(pen='b')
# data = np.random.normal(size=(10,1000))
ptr = 0
x_val,y1_val,y2_val = [0.0]*1000,[0.0]*1000,[0.0]*1000

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

def update():
	global curve1, curve2, data, ptr, p6
	global start_time, bno, qtm, x_val,y1_val,y2_val
	# curve.setData(data[ptr%10])
	curve1.setData(x_val,y1_val)
	curve2.setData(x_val,y2_val)
	# if ptr == 0:
		# p6.enableAutoRange('xy', False)  ## stop auto-scaling after the first data set is plotted
	# ptr += 1



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
