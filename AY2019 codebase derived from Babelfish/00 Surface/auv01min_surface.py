import time
import serial
import threading
import logging
import logging.handlers
from datetime import datetime
from tkinter import *
import RPi.GPIO as GPIO
import json
import os

# GPIO.setmode(GPIO.BCM)
# GPIO.setup(17, GPIO.OUT)
# GPIO.output(17,1)

#                       #
#------Serial Setup-----#
#                       #
ser=serial.Serial(
    port='/dev/ttyACM0',
    baudrate=115200,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1
    )

#                       #
#-----Logging Setup-----#
#                       #
#filename = datetime.now().strftime('./log/AUV_%Y%m%d_%H:%M:%s.log')
filename=datetime.now().strftime('/var/www/auv_logs/AUV_%Y%m%d_%H:%M:%s.log')
log = logging.getLogger()
log.setLevel(logging.INFO)
format = logging.Formatter('%(asctime)s : %(message)s')
file_handler = logging.FileHandler(filename)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(format)
log.addHandler(file_handler)


#                       #
#-----PHP Interfacing-----#
#                       #
overlay = "/dev/shm/mjpeg/user_annotate.txt"
os.system("sudo chmod 777 /dev/shm/mjpeg/user_annotate.txt")
serial_data_directory = "/var/www/html/"


#Set global killswitch event across threads
stop_threads=threading.Event()
quit_window=threading.Event()
stop_persistent_h=threading.Event()
stop_persistent_d=threading.Event()
suppress_commands=threading.Event()
mbed_in_commands=threading.Event()
mbed_in_call=threading.Event()

#lazy ... dont want to change these everywhere
input_string=">> "
error_msg="Invalid entry. Try again."
return_menu="Returning to main menu."
stop_command="STOP"

def horizon():
    writeline=stop_command.encode()
    ser.write(writeline)
    log.info("Raspi command sent: "+writeline.decode())
    #print("sent: "+writeline.decode())
    #print("Event Horizon initiated. Waiting for confirmation from mbed.")
    success=0
    i=0
    while(success==0):
        while(horizon_state==1):
            #if (i==10):
                #print("mbed confirmed entering Event Horizon.")
                #print("System will remain locked out until mbed program releases.")
                #print("Please stand by to stand by.")
            time.sleep(0.001)
            i+=1
        if ((i>0) and (horizon_state==0)):
            #print()
            #print("mbed has returned to normal state.")
            #print("mbed was in Event Horizon state for " + str(i) + " ms.")
            success=1
    #print("This action has been called " + str(horizon_count) + " times.")
    if (horizon_count>4):
        #print("Raspi can only count total 15 events.")
        #print("Recommend restarting mbed after 5 events.")
        #print()
        #print("Do you wish to reset mbed?")
        #print("[y]es or [n]o")
        # success=0
        # reset=0
        # selection=input(input_string)
        # while (success==0):
            # if (selection==stop_command):
                # horizon()
                # success=1
            # elif (selection=='y'):
        success=reset_mbed()

def clear_serial():
    ser.reset_input_buffer()
    time.sleep(0.01)
    try:
        ser.readline()
        return 1
    except UnicodeDecodeError:
        return 0


def reset_mbed():
    #print("Restarting mbed")
    #print("Program may exit due to serial reset")
    #Stop thrusters and set Event flags to inhibit new commands.
    # stop_persistent_h.set()
    # stop_persistent_d.set()
    # stop_thrusters_command()
    #Set Event flag to end serial read thread.
    stop_threads.set()
    #print("Shutting down thrusters and closing serial link.")
    time.sleep(2)
    ser.send_break()     #break command over serial resets mbed
    writeline=('res:000').encode()
    time.sleep(0.1)
    ser.write(writeline)
    log.info("Raspi command sent: "+writeline.decode())
    #print("sent: "+writeline.decode())
    #print("Restarting serial link.")
    #clear Event flags.
    # stop_threads.clear()
    # stop_persistent_h.clear()
    # stop_persistent_d.clear()
    i=0
    while (i<100):
        serialreset=0
        j=0
        while (serialreset==0):
            serialreset=clear_serial()
            j+=1
        i+=1
    #Start reading from serial again.
    start_serial_thread()
    return 1

#For error handling
#ensure user input is int or str before using logic
def isInt(string):
    try: 
        int(string)
        return True
    except ValueError:
        return False
        
def isHex(string):
    try:
        int(string,base=16)
        return True
    except ValueError:
        return False

# Walk through Calibration process.
# mbed is only streaming data; no special pi<>mbed<>bno interaction.
# Cal bits per CALIB_STAT register: 
#   ff - pass final, 3x - pass gyro, x3 - pass mag, xc - pass acc
def set_cal():
    returnval=0
    check_full=0xff
    while (returnval!=1):
        if ((calibration & check_full) == 0xff):
            #print("Calibration completed.")
            #print()
            returnval=1
        elif ((calibration & 0x3f) != 0x3f):
            gyro_check=0x30
            acc_check=0x0c
            mag_check=0x03

            #Accelerometer calibration (0x0c)
            while ((acc_check & calibration)!=acc_check):
                #print()
                #print("Calibrating Accelerometer:")
                #print("Place vehicle in 6 different, orthogonal, and stable positions for a few seconds at a time.")
                #print("Desired: 0x0c, Cal: "+str(hex(calibration)) + ", Mag bits: "+str(hex(calibration&acc_check)))
                time.sleep(0.5)
            #print("Accelerometer calibrated.")

            #Magnetometer calibration (0x03)
            while ((mag_check & calibration)!=mag_check):
                #print()
                #print("Calibrating Magnetometer:")
                #print("Do a barrel roll for magnetometer cal.")
                #print("Desired: 0x03, Cal: "+str(hex(calibration)) + " Mag bits: "+str(hex(calibration&mag_check)))
                time.sleep(0.5)
            #print("Magnetometer calibrated.")

            #Gyroscope calibration (0x30)
            while ((gyro_check & calibration) != gyro_check):
                #print()
                #print("Calibrating Gyroscope:")
                #print("Place vehicle in a stable position for a few seconds at a time.")
                #print("Desired: 0x30, Cal: "+str(hex(calibration)) + ", Mag bits: "+str(hex(calibration&gyro_check)))
                time.sleep(0.5)
            #print("Gyroscope calibrated.")          

        time.sleep(0.02)
    return returnval

def reconstruct_gain(data):
    exponent = (data&0xf)
    scalar = round((data-exponent)/16)
    exponent-=11
    return scalar*(10**exponent)

def reconstruct_pw(data):
    pw=0
    speed_hex=(data & 0xffff)
    speed=(speed_hex/100000)
    if ((data & 0x00010000) == 0x00010000):
        pw=1.5 - speed
    else:
        pw=1.5 + speed
    return pw

def video_overlay():
    nl="\n"
    pw_round=3
    p_pw=str(round(port_pw,pw_round))
    s_pw=str(round(starboard_pw,pw_round))
    f_pw=str(round(fore_pw,pw_round))
    a_pw=str(round(aft_pw,pw_round))
    cal_data=str(hex(calibration))
    status_data=str(hex(status))
    bno_pos=str(status & 0x0007)

    f = round(facing,1)
    r = round(roll,1)
    p = round(pitch,1)
    o = round(offset,1)
    v = round(speed,1)
    m = round(max_speed,1)
    ann1=("f: "+str(f)+", r: "+str(r)+", p: "+str(p)+", o: "+str(o))
    ann2=("port f: "+p_pw+", stbd f: "+s_pw+", port a: "+f_pw+", stbd a: "+a_pw+", cal: "+cal_data)
    annotate = open(overlay, 'w')
    annotate.write("\n" + ann1 + nl + ann2)
    annotate.close()

    json_data={'ser_f':str(f), 'ser_r':str(r), 'ser_p':str(p), 'ser_pf':p_pw, 'ser_sf':s_pw, 'ser_pa':f_pw, 'ser_sa':a_pw, 'ser_cal':cal_data, 'ser_status':status_data, 'fP_gain':str(heading_gain), 'fI_gain':str(pitch_gain), 'fD_gain':str(depth_gain), 'ser_off':str(o), 'ser_vel':str(v), 'ser_max':str(m)}
    serial_data_file = open(serial_data_directory+"surface_JSON", 'w')
    json.dump(json_data,serial_data_file)
    serial_data_file.close()

def shutdownPi():
    log.info("Water leak detected. All systems shutdown.")
    os.system("sudo shutdown -h now")
    log.info("Shutdown for water leak failed. The show goes on.")

def get_angles():
    #Set key values.
    #Keys are first 4 Hexadecimal values in line
    #and used to "tag" what kind of data follows
    ver_key=0x1234
    status_key=0xffff  #also 'ready'
    horizon_key=0xff00
    cal_key=0xc000
    h_key=0xc100
    r_key=0xc300
    p_key=0xc500
    port_key=0xf100
    starboard_key=0xf200
    fore_key=0xf300
    aft_key=0xf400
    h_gain_key=0xd110
    p_gain_key=0xd120
    d_gain_key=0xd130

    #Set globals accessible outside this thread
    global status
    global calibration
    global facing
    global roll
    global pitch
    global offset
    global speed
    global max_speed
    global horizon_count
    global horizon_state
    global port_pw
    global starboard_pw
    global fore_pw
    global aft_pw
    global heading_gain
    global pitch_gain
    global depth_gain

    #Initialize values to 0
    status,calibration,facing,roll,pitch,offset,speed,max_speed=0,0,0,0,0,0,0,0
    port_pw,starboard_pw,fore_pw,aft_pw=0,0,0,0
    horizon_count,horizon_state=0,0
    key,st,cal,h,r,p,d=0x0,0x0,0x0,0x0,0x0,0x0,0x0
    port,star,fore,aft=0,0,0,0
    h_gain,p_gain,d_gain=0,0,0
    
    #See mbed code. Roll and Pitch are +/- 180 from BNO
    #Offset allows mbed and raspi to deal strictly with
    #positive numbers.
    #360 deg added on mbed side, must be subtracted
    offset=0x1680

    #mbed sends 8bit words, +1 for overhead
    word_size=9

    #mbed sends 11 8bit words every 20ms
    #Or one word around every 2ms
    #This while loop only processes 1 word at a time
    while not stop_threads.is_set(): 
        #Only proceed if there are bytes in Serial waiting to be read
        while (ser.inWaiting==0):
            time.sleep(0.005)
            #print("no serial input... waiting")

        #Read bytes from Serial
        in_buffer=ser.readline()
        
        #Only assign prefix and data if serial line is correct length
        #Prevents Value Errors
        int_buffer_prefix=0x10000
        int_buffer_data=0x10000
        length=len(in_buffer)
        if (length==word_size):
            str_buffer_prefix=in_buffer[0:2].decode()+in_buffer[2:4].decode()
            ##print("prefix: "+str(str_buffer_prefix))
            if isHex(str_buffer_prefix):
                int_buffer_prefix=int(str_buffer_prefix,base=16)
            str_buffer_data=in_buffer[4:6].decode()+in_buffer[6:8].decode()
            ##print("str prefix: " + str(str_buffer_prefix)+ ", data: "+str(str_buffer_data))
            if isHex(str_buffer_data):
                int_buffer_data=int(str_buffer_data,base=16)
            ##print("int prefix: " + str(hex(int_buffer_prefix)) + ", data: " + str(hex(int_buffer_data)))
        
        elif (in_buffer[0:3].decode()=='log'):
            log.info(in_buffer[0:(length-2)].decode())
        else:
            log.debug(in_buffer[0:(length-2)].decode())

        #Sort data to correct variable using the keys
        if (int_buffer_prefix == ver_key):
            key=int_buffer_data
            ##print("key detected")
        if (int_buffer_prefix == status_key):
            ##print("status detected")
            st=int_buffer_data
            horizon_state=0
        if ((int_buffer_prefix & 0xfff0)==horizon_key):
            ##print("horizon detected")
            st=int_buffer_data
            horizon_count=(int_buffer_prefix & 0x000f)
            horizon_state=1
        if (int_buffer_prefix == cal_key):
            cal=int_buffer_data
            ##print("cal detected")
        if (int_buffer_prefix == h_key):
            h= int_buffer_data/16
            ##print("heading detected")
        if (int_buffer_prefix == r_key):
            r=(int_buffer_data-offset)/(0x10)
            ##print("roll detected")
        if (int_buffer_prefix == p_key):
            p=(int_buffer_data-offset)/(0x10)
            ##print("pitch detected")
        # if (int_buffer_prefix == d_key):
            # d=(int_buffer_data/0x20)
            
        #Filter for and read in PWM values.
        if ((int_buffer_prefix&0xfff0) == port_key):
            port=reconstruct_pw((int_buffer_prefix*0x10000)+int_buffer_data)
        if ((int_buffer_prefix&0xfff0) == starboard_key):
            star=reconstruct_pw((int_buffer_prefix*0x10000)+int_buffer_data)
        if ((int_buffer_prefix&0xfff0) == fore_key):
            fore=reconstruct_pw((int_buffer_prefix*0x10000)+int_buffer_data)
        if ((int_buffer_prefix&0xfff0) == aft_key):
            aft=reconstruct_pw((int_buffer_prefix*0x10000)+int_buffer_data)
            
        # Filter for and read in Gain values.
        if (int_buffer_prefix==h_gain_key):
            h_gain=reconstruct_gain(int_buffer_data)
            #print("hgain: "+str(h_gain))
        if (int_buffer_prefix==p_gain_key):
            print("pgain: "+str(p_gain))
            p_gain=reconstruct_gain(int_buffer_data)
        if (int_buffer_prefix==d_gain_key):
            d_gain=reconstruct_gain(int_buffer_data)
            print("dgain: "+str(d_gain))

#Only update globals after key is verified
        if (key==0xabcd):
            ##print("VERIFIED")
            heading = h
            roll = r
            pitch = p
            calibration=cal
            status=st
            depth=d
            port_pw=port
            starboard_pw=star
            fore_pw=fore
            aft_pw=aft
            heading_gain=h_gain
            pitch_gain=p_gain
            depth_gain=d_gain
            delimiter=':|:'
            logline=delimiter+str(h)+delimiter+str(r)+delimiter+str(p)+delimiter+str(hex(cal))+delimiter+str(hex(st))+delimiter+str(d)+delimiter+str(port_pw)+delimiter+str(starboard_pw)+delimiter+str(fore_pw)+delimiter+str(aft_pw)+delimiter+str(heading_gain)+delimiter+str(pitch_gain)+delimiter+str(depth_gain)
            video_overlay()
            #reset verifications for next loop
            ##print ("cal:" + str(cal) + " heading:"+str(h)+" roll:"+str(r)+" pitch:"+str(p))
            log.info(logline)
            key=0x0
            if  (status & 0x0800) == 0x0800:
                shutdownPi()
        time.sleep(0.0002)

def stop_thrusters_command():
    writeline=('sto:000').encode()
    ser.write(writeline)
    #GPIO.output(40,1)
    #print("sent: "+writeline.decode())
    log.info("Raspi command sent: "+writeline.decode())

#Main menu
#outsource selection to individual functions
def main():
    quit=0
    persistent_h=0
    persistent_d=0
    logline='KEY: heading:|:roll:|:pitch:|:BNO cal:|:status:|:depth:|:port pw:|:starboard pw:|:fore pw:|:aft pw:|:H gain:|:P gain:|:D gain'
    log.info(logline)
    while (quit!=1):
        get_angles()

main()
