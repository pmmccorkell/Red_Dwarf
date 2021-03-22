from time import time,sleep

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

i = 0

ticker_rate = 0.02
def myController():
	global i
	i+=1
	print("controller ran: "+str(i))

def main():
	#while(1):
	ticker(ticker_rate,myController)

main()

