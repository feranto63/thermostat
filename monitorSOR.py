#!/usr/bin/env python

# timeout in seconds betwen reading temperature from sensors
TIMEOUT = 60

import sqlite3
import threading
import os
import glob

import time

import serial
import requests

# global variables
DHT_PIN = 4

#Sqlite Database where to store readings
dbname='/var/www/templog.db'

#Serial devices
DEVICE = '/dev/ttyS0'
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


def main():
	tokenpath = os.path.dirname(os.path.realpath(__file__)) + "/token"
	try:
    		tokenFile = open(tokenpath,'r')
    		TOKEN = tokenFile.read().strip()
    		tokenFile.close()
	except IOError: 
    		print("Non ho trovato il file di token. E' necessario creare un file 'token' con la token telegram per il bot. In ogni caso questo file NON deve essere tracciato da git - viene ignorato perche' menzionato nel .gitignore.")
    		exit()

	print("caricata token.")
	try:
    		chatidFile = open(chatidpath,'r')
    		CHAT_ID = chatidFile.read().strip()
    		chatidFile.close()
	except IOError:
    		print("Non ho trovato il file di chatId. E' necessario creare un file 'chatid' con la chatid telegram per il bot")	
	
	######## inizializza il bot Telegram ###########
	bot = telepot.Bot(TOKEN)

	while True:
    		now = time.time()
    		localtime = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        	deviceID, msgType, value = get_temp_radio()
        	if deviceID != '??':
            		print "ID="+deviceID+",msgType="+msgType+",value="+str(value)
            		if msgType=="TEMP":
	            		log_temp_radio(localtime,deviceID,msgType,value)
				######## scrive il file del sensore 1        
    				f = open("sensor1.log","w")  #apre il file dei dati in read mode
    				f.write(localtime+" "+str(value)+"\n")  #legge la info del sensore sul file e divide per data, ora e valore
    				f.close()  #chiude il file dei dati e lo salva
			elif msgType=="BATT":
				message="La batteria del sensore con ID:"+str(deviceID)+" e' "
				if value==0:
					message+="bassa"
				else:
					message+=str(value)
				print(message)
				bot.sendMessage(CHAT_ID, message,disable_notification=True)
			elif msgType=="SLEE":
				message="La batteria del sensore con ID:"+str(deviceID)+" e' "
				if value==0:
					message+="bassa"
				else:
					message+=str(value)
				print(message)

        	time.sleep(5*60)

if __name__=="__main__":
    	main()
