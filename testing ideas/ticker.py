from time import sleep, time

# user watsonic posted on 8/7/2020
# https://stackoverflow.com/questions/8600161/executing-periodic-actions-in-python
# def ticker(period,f,*args):
def ticker(period,f):
	def g_tick():
		t = time()
		while True:
			t += period
			yield max(t  - time(),0)
	g = g_tick()
	while True:
		sleep(next(g))
#		f(*args)
		f()
