

HEAT_ID =31 #da leggere da file di configurazione

dbname='/var/www/templog.db'


import sqlite3

# store the temperature in the database
def log_w_sensor (t_stamp, node_id, temp, humid):   #orario,temp, tempDHT, humidity, ExtTemp, HeatOn, TargetTemp)

    conn=sqlite3.connect(dbname)
    curs=conn.cursor()
    dati_da_inserire = [t_stamp, node_id, temp, humid]  #orario,temp,tempDHT,humidity, ExtTemp, HeatOn, TargetTemp]
    curs.execute("INSERT INTO w_temps values (?,?,?,?)", dati_da_inserire)
    # commit the changes
    conn.commit()
    conn.close()
    return()


				
def save_sensorlog(filename, t_stamp, temp, humidity):
    filesensor = open(filename,"w")  #apre il file di log del sensore in write mode, se il file non esiste lo crea
    #####   print (( 'Temp={0:0.1f}*C  Humidity={1:0.1f}%'.format(temperature, humidity)))
    filesensor.write(t_stamp +" "+str(temp)+" "+str(humidity))
    filesensor.close()  #chiude il file dei dati e lo salva

			
##############################################

import sys
import time
import telepot
import string
import random
import os
import sys
import subprocess

import urllib3

# posto retry = 3 per evitare exception sul send.message casuale
telepot.api._pools = {
    'default': urllib3.PoolManager(num_pools=3, maxsize=10, retries=3, timeout=30),
}

#imports for thermometer reading
import os
import glob
#imports for gmail reading
import imaplib
import email

#import library for logging
"""import logging
logging.basicConfig(
        filename='/home/pi/BotMysController.log',
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.WARN)
"""

sensor = [['2000-01-01 00:00:00',0.0, 0.0] for x in range (100)]

def MySensorEvent(message):
    global ALARM_STATUS, sensor, MaggiordomoID
    """Callback for mysensors updates."""

    orario = time.localtime(time.time())
    #localtime = time.asctime( orario )
    localtime = time.strftime("%Y-%m-%d %H:%M:%S", orario)
    ora_minuti = time.strftime("%H:%M", orario)
	
    print("sensor_update " + str(message.node_id))
    print("message.sub_type: "+str(message.sub_type))
    print("message.payload: "+message.payload)
	
    PAYLOAD = message.payload
    if message.node_id == 30:
        print("message.node_id == 30")
        if message.sub_type == 16:
            print("message.sub_type == 16")
            print("PAYLOAD = "+str(PAYLOAD))
            if int(PAYLOAD) == ALARM_STATUS:
                print("message.payload == "+str(ALARM_STATUS))
                return()
            else:
                ALARM_STATUS = int(PAYLOAD)
                if int(PAYLOAD) == 0:
                    print("PAYLOAD == 0")
                    bot.sendMessage(CHATID,"Sono "+MaggiordomoID+". E' scattato l'antifurto alle "+localtime)
                else:
                    print("PAYLOAD == 1")
                    bot.sendMessage(CHATID,"Sono "+MaggiordomoID+". L'antifurto si e' spento alle "+localtime)
    else:
        print("node_id="+str(message.node_id))
        if int(message.sub_type) == 0: #it is a temperature
            sensor[message.node_id][1] = float(PAYLOAD)
            sensor[message.node_id][0] = localtime
            print("it's temperature")
        else:
            if int(message.sub_type) == 1: # it is a humidity
                sensor[message.node_id][2] = float(PAYLOAD)
                sensor[message.node_id][0] = localtime
                print("it's humidity")

        print("test")
        sensorfilename = "sensor"+str(message.node_id)+".log"
        
        if MaggiordomoID == "Battista":
            if message.node_id == 8: #soggiorno
                sensorfilename = "sensor1.log"
            else:
                if message.node_id == 31: #giardino
                    sensorfilename = "sensor2.log"
                else:
                    sensorfilename = "sensor"+str(message.node_id)+".log"
        else:
            if MaggiordomoID == "Ursula":
                if message.node_id == 15: #zona notte
                    sensorfilename = "sensor1.log"
                else:
                    sensorfilename = "sensor"+str(message.node_id)+".log"
            else:
                if MaggiordomoID == "Ambrogio":
                    if message.node_id == 5: #giardino
                        sensorfilename = "sensor1.log"
                    else:
                        if message.node_id == 4: #zona notte
                            sensorfilename = "sensor2.log"
                        else:
                            if message.node_id == 10: # cucina
                                sensorfilename = "sensor3.log"
                else:
                    sensorfilename = "sensor"+str(message.node_id)+".log"
        print("sensorfilename ="+sensorfilename)
        print("timestamp="+sensor[message.node_id][0])
        print("temp="+str(sensor[message.node_id][1]))
        print("Humidity="+str(sensor[message.node_id][2]))
        save_sensorlog(sensorfilename, sensor[message.node_id][0], sensor[message.node_id][1], sensor[message.node_id][2])
    return()


######## legge da file lo stato del riscaldamento e dello standby ###########
def read_heating_status():
	try:
		f = open("heating_status","r")  #apre il file dei dati in read mode
		h_status=f.read().strip()   #legge la info di presence sul file
		f.close()  #chiude il file dei dati e lo salva
		if h_status == "ON":
			heating_status = True
		else:
			heating_status = False
	except IOError:
		heating_status = False  #se il file non e' presente imposto la presence a False
	return(heating_status)

def read_heating_standby():
	try:
		f = open("heating_standby","r")  #apre il file dei dati in read mode
		hby_status=f.read().strip()   #legge la info di presence sul file
		f.close()  #chiude il file dei dati e lo salva
		if hby_status == "ON":
			heating_standby = True
		else:
			heating_standby = False
	except IOError:
		heating_standby = False  #se il file non e' presente imposto la presence a False
	return(heating_standby)

#################### accende o spegne i termosifoni #############
def TurnON_termosifoni(heatID):
	GATEWAY.set_child_value(heatID, 1, 2, 1)
	return()

def TurnOFF_termosifoni(heatID):
	GATEWAY.set_child_value(heatID, 1, 2, 0)
	return()

############ legge da file il token del Telegram Bot e della chat id

tokenpath = os.path.dirname(os.path.realpath(__file__)) + "/BotAssistant.token"
IDpath= os.path.dirname(os.path.realpath(__file__)) + "/Maggiordomo.ID"
chatidpath = os.path.dirname(os.path.realpath(__file__)) + "/BotAssistant.chatid"
#chatidgatepath = os.path.dirname(os.path.realpath(__file__)) + "/chatid_cancello"


try:
    tokenFile = open(tokenpath,'r')
    TOKEN = tokenFile.read().strip()
    tokenFile.close()
except IOError: 
    #logging.error("Non ho trovato il file di token. E' necessario creare un file 'BotAssistant.token' con la token telegram per il bot. In ogni caso questo file NON deve essere tracciato da git - viene ignorato perche' menzionato nel .gitignore.")
    exit()

#logging.info("caricata token.")

try:
    chatidFile = open(chatidpath,'r')
    CHATID = chatidFile.read().strip()
    chatidFile.close()
except IOError: 
    #logging.error("Non ho trovato il file di chatid. E' necessario creare un file 'BotAssistant.chatid' con la chatidi telegram per il bot. In ogni caso questo file NON deve essere tracciato da git - viene ignorato perche' menzionato nel .gitignore.")
    exit()

#logging.info("caricata chatid.")

# CHATID = 26228522

#def handle(msg):
#    flavor = telepot.flavor(msg)
#
#    summary = telepot.glance(msg, flavor=flavor)
#    print (flavor, summary)



bot = telepot.Bot(TOKEN)
# bot.message_loop(handle)
print ('running Sensor Controller ...')

myIPaddress = str(subprocess.check_output(['dig','+short','myip.opendns.com','@resolver1.opendns.com']))

import mysensors.mysensors as mysensors

ALARM_STATUS = 1


		############### WORKING HERE ##################

GATEWAY = mysensors.SerialGateway('/dev/ttyMySensorsGateway', MySensorEvent, persistence=True,
  persistence_file='/home/pi/git/thermostat/thermostat/mysensors.pickle')
GATEWAY.start()


# generate a name for this maggiordomo if does not exist
try:
    MaggiordomoIDFile = open(IDpath,'r')
    MaggiordomoID = MaggiordomoIDFile.read().strip()
    MaggiordomoIDFile.close()
#    bot.sendMessage(CHATID, "sono "+MaggiordomoID+". Mi sono appena svegliato")

except IOError: 
    #logging.error("Non ho trovato il file con ID del maggiordomo. Genero ID e lo salvo")
    MaggiordomoID = "Maggiordomo-"+''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(10)) #da generare in modo random
    MaggiordomoIDFile = open(IDpath,'w')
    MaggiordomoIDFile.write(MaggiordomoID)
    MaggiordomoIDFile.close()

#    bot.sendMessage(CHATID,"sono "+MaggiordomoID+". Sono stato appena generato")

bot.sendMessage(CHATID,"Sono "+MaggiordomoID+". Inizio il monitoraggio dell'antifurto", disable_notification=True)

HEAT_STATUS = read_heating_status()
print("initial heat status"+HEAT_STATUS)


#restore acensione riscaldamento
if HEAT_STATUS:
	TurnON_termosifoni(HEAT_ID)
else:
	TurnOFF_termosifoni(HEAT_ID)

# Keep the program running.
while 1:
	CURRENT_HEAT=read_heating_status()
	if CURRENT_HEAT != HEAT_STATUS:
		if CURRENT_HEAT:
			TurnON_termosifoni(HEAT_ID)
		else:
			TurnOFF_termosifoni(HEAT_ID)
		HEAT_STATUS = CURRENT_HEAT
	time.sleep(1)
