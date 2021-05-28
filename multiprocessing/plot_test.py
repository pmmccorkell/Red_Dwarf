from threading import Thread
from time import sleep, time
import pandas as pd
import matplotlib as plt

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



def plotting():
	hea_dict = 
	hea_plot = pd.DataFrame()


	# data_frames = read_csv()

	# Iterate through the list[] of Data Frames.
	# for data_frame in data_frames:
		# Plot each Data Frame separately. Assigning the x-axis and y-axis as it is on the Oscope.
		# data_frame.plot(x='time',y='voltage')

	# plt.show()



def setup():
	plot_thread = Thread(target=plotting,daemon=True)
	plot_thread.start()

setup()

