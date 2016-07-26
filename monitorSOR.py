#!/usr/bin/env python

# timeout in seconds betwen reading temperature from sensors
TIMEOUT = 60


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
DEVICE = '/dev/ttyS0'
#DEVICE = '/dev/tty.Bluetooth-Incoming-Port'
BAUD = 9600

ser = serial.Serial(DEVICE, BAUD)


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
def get_temp_radio():
    global ser

	#Timeout (in s) for waiting to read a temperature from RF sensors
    TIMEOUT = 30
    tempvalue = -100
    deviceid = '??'
    voltage = 0
    msgType = 'NULL'

    fim = time.time()+ TIMEOUT
    while (time.time()<fim) and (tempvalue == -100):
        n = ser.inWaiting()
        if n != 0:
            data = ser.read(n)
            nb_msg = len(data) / 12
            for i in range (0, nb_msg):
                msg = data[i*12:(i+1)*12]
		print("ser.inWaiting= "+str(i))
		print("Data= "+str(msg))
		deviceid = msg[1:3]
		print("Device ID is= "+str(deviceid))
		if msg[0] != "a":
			print("First letter doesn't equal a. Flushing...")
			ser.flushInput()
			return
		if len(msg) != 12:
			print("Message length not 12. Flushing...")
			ser.flushInput()
			return
		msgType = msg[3:7]
		if msgType == "TEMP":
			tempvalue = float(msg[7:])
			print("Temp msg= "+str(tempvalue))
		if msgType == "BATT":
			if msg[7:10] == "LOW":
				tempvalue = 0
			else:
				tempvalue = float(msg[7:11])
			print("Bat msg= "+str(tempvalue))
    return (deviceid,msgType,tempvalue)


########## gestione sensori Radio CISECO ###############
#import serial


#def get_temp_radio():
#    DEVICE = '/dev/ttyAMA0'
#    BAUD = 9600

#    ser = serial.Serial(DEVICE, BAUD)
#    n = ser.inWaiting()
#    if n != 0:
#        msg = ser.read(n)
#        deviceID = msg[1:3]
#        messType = msg[3:7]
#        value = msg[7:12]
#    else:
#        deviceID = "--"
#        messType = "NULL"
#        value = 0
#    return deviceID, messType, value
    
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
#    	CurTemp = read_temp()
#    	if CurHumidity == None:
#        	CurHumidity = 'N.A.'
#        CurTempDHT, CurHumidity = read_TandH()
        deviceID, msgType, value = get_temp_radio()
        #apre il file dei dati in append mode, se il file non esiste lo crea
        #filedati = open("filedati","a")
        #scrive la temperatura coreente ed il timestam sul file
        #filedati.write("T="+str(CurTemp)+",HR="+str(CurHumidity)+"@"+localtime+"\n")
        if deviceID != '??':
        #    filedati.write("ID="+deviceID+",msgType="+msgType+",value="+str(value))
            log_temp_radio(localtime,deviceID,msgType,value)
            print "ID="+deviceID+",msgType="+msgType+",value="+str(value)
        #chiude il file dei dati e lo salva
        #filedati.close()
        #log_temperature(localtime,CurTemp,CurTempDHT,CurHumidity)
        
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
