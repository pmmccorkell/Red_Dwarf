# Settings specific to network configuration
# Only uncomment 1 line for each variable


mqtt_broker = '127.0.0.1'       # loopback
#mqtt_broker = '192.168.5.4'    #SURFnet IP
# pick a unique clientname to prevent collisions with other clients
# Only uncomment one, depending on which server you desire.
# sub_clientname="mydesk"			# Pat's desk
# sub_clientname="surfpi_sub"		# SURF Pi
# sub_clientname="reddwarf"		# submarine
sub_clientname="overhead_qtm"   # SURF underwater NUC

# pick a unique clientname to prevent collisions with other clients
# Only uncomment one, depending on which server you desire.
# pub_clientname="underwater_qtm"   # SURF underwater NUC
pub_clientname="overhead_pub"   # SURF overhead NUC

#
# Pick the default folder for environment / OS you're running in.
# Only uncomment one, depending on server configuration.
#
default_folder="/mnt/c/Python/Qualisys_MQTT"		# WSL on Win10
#default_folder="/home/pi/mqtt/"	                # RasPi
#default_folder="/Users/Levi DeVries/Downloads/"    #Win10

# qtm_server = '10.0.0.118'      # old IP
qtm_server='127.0.0.1'          # loopback
# qtm_server='192.168.5.4'       # SURFnet IP
# qtm_server='10.60.17.244'       # TSD office computer

#DEBUGGING=0
DEBUGGING=1
