from pwmControl import *
from time import sleep
from pid import PID
from math import sin, cos
from math import tau as twopi

############## PID Setup ##############

ticker_Rate = 0.02		# seconds

az_tolerance = 2		# degrees
heading_Kp = 0.008333	
heading_Ki = 0.0		
heading_Kd = 0.0		
pidHeading = PID(heading_Kp,heading_Ki,heading_Kd,ticker_rate,az_tolerance)

# import:
######## LEAK DETECT ########

######### Intake Commands ######

 ### stop all persistent ###
persistent_heading=-1
persistent_speed=-1
persistent_offset=-1

heading = 0xffff
pitch = 0xffff
roll = 0xffff

commands = {
	'hea' :  ,
	'vel' :  ,
	'off' :  ,
	'sto' :  ,
#	'res' :  ,
#	'dep' :  ,
	'hkp' :  ,
	'hki' :  ,
	'hkd' :  
}

####### what triggers event horizon #####
    ### look horizon ###



######## Az Controller #########

def headingController():
	speed=0
	desired_heading=persistent_heading
	current_heading=heading
	if (desired_heading != -1):
		diff = abs(desired_heading-current_heading)
		if (diff>180):
			if (desired_heading>180):
				current_heading=current_heading+180
				desired_heading=desired_heading-180
			else:
				current_heading=current_heading-180
				desired_heading=desired_heading+180
		speed = pidHeading.process(desired_heading,current_heading)

	# if ((abs(speed)<minThrusterBias) and (abs(diff)>az_tolerance)):
	# 	if (speed<0):
	# 		speed=(-1(minThrusterBias))
	# 	else:
	# 		speed=minThrusterBias

	return speed

def trigSpeedController():
	desired_speed = {
		'cos' : 0,
		'sin' : 0
	}
	if (persistent_offset != -1):
		# convert to radians
		offset_factor = (twopi / 360) * persistent_offset
	
		# add 45deg to offset for motors being angled
		offset_factor += (twopi/8)

		# transform the forward speed to trig
		desired_speed['cos'] = (persistent_speed * cos(offset_factor))/1000
		desired_speed['sin'] = (persistent_speed * sin(offset_factor))/1000
	return desired_speed


def azThrusterLogic():
	# if (persistent_speed==-1):
	# 	cos_speed = 0
	# 	sin_speed = 0
	# else:
	trig_speed=trigSpeedController()
	# if (persistent_heading==-1):
	# 	heading_speed=0
	# else:
	heading_speed = headingController()


	fwd_star_speed=(trig_speed['cos'] - heading_speed);
	aft_port_speed=(trig_speed['cos'] + heading_speed);
	fwd_port_speed=(trig_speed['sin'] + heading_speed);
	aft_star_speed=(trig_speed['sin'] - heading_speed);

def clampESC(n, minn, maxn):
	return min(max(n, minn), maxn)

def stopAllPersistent():
	persistent_heading=-1
	persistent_offset=-1
	persistent_speed=-1
	pidHeading.clear()




