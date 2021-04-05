#
# IPs for different MQTT server Pis.
# Only uncomment one, depending on which server you desire.
#
# server='127.0.0.1'	# loopback
# server="172.30.35.102"	# Pat's desk
# server="172.30.38.181"	# SURF nonet
# server="192.168.5.4"      # SURFnet internal
server = '10.60.5.238'      # SURFnet external

# pick a unique clientname to prevent collisions with other clients
# Only uncomment one, depending on which server you desire.
# clientname="mydesk"			# Pat's desk
# clientname='surfpi_sub'		# SURF
clientname="RedDwarf"		# submarine

# default_directory='/Users/Levi DeVries/Downloads/'
# default_directory='/mnt/c/Python/Qualisys_MQTT/log/'
default_directory='/mnt/c/Python/Qualisys_MQTT/log/'
# default_directory = '/home/pi'


DEBUGGING=0
#DEBUGGING=1

