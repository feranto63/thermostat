#!/usr/bin/env python

import sqlite3
import threading
import os
import glob

import time
#import urllib2
#import urllib

import serial
import requests



# global variables
DHT_PIN = 4

#remote database page
#remotedb = 'http://www.lourenco.eu/temperature/savedb.php'

#Sqlite Database where to store readings
dbname='/var/www/templog.db'

#Serial devices
DEVICE = '/dev/ttyAMA0'
#DEVICE = '/dev/tty.Bluetooth-Incoming-Port'
BAUD = 9600

ser = serial.Serial(DEVICE, BAUD)

#Timeout (in s) for waiting to read a temperature from RF sensors
TIMEOUT = 30

#Weather Underground Data
WUKEY = ''
STATION = ''
#Time between Weather Underground samples (s)
SAMPLE = 10*60

def log_temperature(orario,temp, tempDHT, humidity):

    conn=sqlite3.connect(dbname)
    curs=conn.cursor()
    dati_da_inserire = [orario,temp,tempDHT,humidity]
    curs.execute("INSERT INTO temps values (?,?,?,?)", dati_da_inserire)
    # commit the changes
    conn.commit()
    conn.close()
    
def log_temp_radio(orario,deviceID,msgType,temp):

    conn=sqlite3.connect(dbname)
    curs=conn.cursor()
    dati_da_inserire = [orario,deviceID,msgType,temp]
    curs.execute("INSERT INTO temp_radio values (?,?,?,?)", dati_da_inserire)
    # commit the changes
    conn.commit()
    conn.close()

# get temperature
# returns -100 on error, or the temperature as a float
def get_temp():
    global ser

    tempvalue = -100
    deviceid = '??'
    voltage = 0

    fim = time()+ TIMEOUT

    while (time()<fim) and (tempvalue == -100):
        n = ser.inWaiting()
        if n != 0:
            data = ser.read(n)
            nb_msg = len(data) / 12
            for i in range (0, nb_msg):
                msg = data[i*12:(i+1)*12]

            	deviceid = msg[1:3]

                if msg[3:7] == "TMPA":
                    tempvalue = msg[7:]

                if msg[3:7] == "BATT":
                    voltage = msg[7:11]
                    if voltage == "LOW":
                        voltage = 0
        else:
            sleep(5)

    return {'temperature':tempvalue, 'id':deviceid}

################# gestione della interfaccia di GPIO   
# wiringpi numbers  
import RPi.GPIO as GPIO
##import wiringpi2 as wiringpi
##wiringpi.wiringPiSetup()
##wiringpi.pinMode(0, 1) # sets WP pin 0 to output
GPIO.setmode(GPIO.BCM)
#GPIO.setup(HEAT_PIN,GPIO.OUT)
#GPIO.setup(GATE_PIN,GPIO.OUT)

#Find temperature from thermometer
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_c #, temp_f

################## lettura del sensore DHT 11 temperatura e umidita'
import Adafruit_DHT

# Sensor should be set to Adafruit_DHT.DHT11,
# Adafruit_DHT.DHT22, or Adafruit_DHT.AM2302.
def read_TandH():
    global DHT_PIN
    sensor = Adafruit_DHT.DHT22
    # Example using a Raspberry Pi with DHT sensor
    # connected to GPIO4.
    pin = DHT_PIN
    
    # Try to grab a sensor reading.  Use the read_retry method which will retry up
    # to 15 times to get a sensor reading (waiting 2 seconds between each retry).
    humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
    
    # Note that sometimes you won't get a reading and
    # the results will be null (because Linux can't
    # guarantee the timing of calls to read the sensor).
    # If this happens try again!
    if humidity is not None and temperature is not None:
        print 'Temp={0:0.1f}*C  Humidity={1:0.1f}%'.format(temperature, humidity)
        return (temperature, humidity)
    else:
        print 'Failed to get reading. Try again!'
        return (None, None)

########## fine gestione sensore DHT11 ############################

########## gestione sensori Radio CISECO ###############
#import serial


def get_temp_radio():
    DEVICE = '/dev/ttyAMA0'
    BAUD = 9600

    ser = serial.Serial(DEVICE, BAUD)
    n = ser.inWaiting()
    if n != 0:
        msg = ser.read(n)
        deviceID = msg[1:3]
        messType = msg[3:7]
        value = msg[7:12]
    else:
        deviceID = "--"
        messType = "NULL"
        value = 0
    return deviceID, messType, value
    
################### fine gestione sensori Radio CISECO ##############

#def get_temp_wu():
#    try:
#        conn=sqlite3.connect(dbname)
#        curs=conn.cursor()
#        query = "SELECT baudrate, porta, id, active FROM sensors WHERE id like'W_'"
#
#        curs.execute(query)
#        rows=curs.fetchall()

#        conn.close()
        
#        if rows != None:
#            for row in rows[:]:
#                WUKEY = row[1]
#                STATION = row[0]

#                if int(row[3])>0:
#                    try:
#                        r = requests.get("http://api.wunderground.com/api/{0}/conditions/q/{1}.json".format(WUKEY, STATION))
#                        data = r.json()
#                        log_temperature({'temperature': data['current_observation']['temp_c'], 'id': row[2]})
#                    except Exception as e:
#                        raise

#    except Exception as e:
#        text_file = open("debug.txt", "a+")
#        text_file.write("{0} ERROR:\n{1}\n".format(strftime("%Y-%m-%d %H:%M:%S", gmtime()),str(e)))
#        text_file.close()

# main function
# This is where the program starts 


def main():
#    get_temp_wu()
#    t =threading.Timer(SAMPLE,get_temp_wu)
#    t.start()
    CurHumidity = 0

    while True:
    	now = time.time()
    	#localtime = time.asctime( time.localtime(now) )
    	localtime = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
#    	CurTargetTemp=current_target_temp()
    	CurTemp = read_temp()
    	if CurHumidity == None:
        	CurHumidity = 'N.A.'
        CurTempDHT, CurHumidity = read_TandH()
        deviceID, msgType, value = get_temp_radio()
        #apre il file dei dati in append mode, se il file non esiste lo crea
        filedati = open("filedati","a")
        #scrive la temperatura coreente ed il timestam sul file
        filedati.write("T="+str(CurTemp)+",HR="+str(CurHumidity)+"@"+localtime+"\n")
        if deviceID != '--':
            filedati.write("ID="+deviceID+",msgType="+msgType+",value="+str(value))
            log_temp_radio(localtime,deviceID,msgType,value)
            print "ID="+deviceID+",msgType="+msgType+",value="+str(value)
        #chiude il file dei dati e lo salva
        filedati.close()
        log_temperature(localtime,CurTemp,CurTempDHT,CurHumidity)
        
#        if temperature['temperature'] != -100:
#            print ("temperature="+str(temperature))#

            # Store the temperature in the database
#            log_temperature(temperature)
#        else:
#            print ("temperature=ERROR-Timeout!")

        #if t.is_alive() == False:
        #    t =threading.Timer(SAMPLE,get_temp_wu)
        #    t.start()
        time.sleep(5*60)

if __name__=="__main__":
    main()
