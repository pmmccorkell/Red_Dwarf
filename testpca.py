import pca9685
import busio
from board import SCL,SDA
from time import sleep

i2c = busio.I2C(SCL,SDA)
pca = pca9685.PCA9685(i2c)

def main():
	pca.freq(50)
	i=0
	while(i<12):
#		pca.duty(0,1833)		# 1.1ms	400Hz
		pca.duty(0,225)			# 1.1ms 50Hz
		print(str(pca.duty(0)))
		sleep(3)
#		pca.duty(0,2500)		# 1.5ms 400Hz
		pca.duty(0,306)			# 1.5ms 50Hz
		print(str(pca.duty(0)))
		sleep(3)
#		pca.duty(0,3167)		# 1.9ms 400Hz
		pca.duty(0,388)			# 1.9ms 50Hz
		print(str(pca.duty(0)))
		sleep(3)
		i+=1
