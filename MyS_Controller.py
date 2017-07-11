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
import logging
logging.basicConfig(
        filename='/home/pi/BotMysController.log',
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.WARN)

sensor = [][3]

def MySensorEvent(message):
    global ALARM_STATUS, sensor
    """Callback for mysensors updates."""

    orario = time.localtime(time.time())
    localtime = time.asctime( orario )
    ora_minuti = time.strftime("%H:%M", orario)
	
    print("sensor_update " + str(message.node_id))
    print("message.sub_type: "+str(message.sub_type))
    print("message.payload: "+message.payload)
	
    if message.node_id == 3:
       print("message.node_id == 3")
       if message.sub_type == 16:
           print("message.sub_type == 16")
           PAYLOAD = int(message.payload)
           print("PAYLOAD = "+str(PAYLOAD))
           if PAYLOAD == ALARM_STATUS:
               print("message.payload == "+str(ALARM_STATUS))
               return()
           else:
               ALARM_STATUS = PAYLOAD
               if PAYLOAD == 0:
                   print("PAYLOAD == 0")
                   bot.sendMessage(CHATID,"Sono "+MaggiordomoID+". E' scattato l'antifurto")
               else:
                   print("PAYLOAD == 1")
                   bot.sendMessage(CHATID,"Sono "+MaggiordomoID+". L'antifurto si e' spento")
    else:
        if message.sub_type == 0: #it is a temperature
            sensor[message.node_id][1] = float(PAYLOAD)
            sensor[message.node_id][0] = localtime
        elif message.sub_type == 1: # it is a humidity
            sensor[message.node_id][2] = float(PAYLOAD)
            sensor[message.node_id][0] = localtime

        sensorfilename = "sensor"+str(message.node_id)+".log"
        save_sensorlog(sensorfilename, sensor[message.node_id][0], sensor[message.node_id][1], sensor[message.node_id][2])
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
    logging.error("Non ho trovato il file di token. E' necessario creare un file 'BotAssistant.token' con la token telegram per il bot. In ogni caso questo file NON deve essere tracciato da git - viene ignorato perche' menzionato nel .gitignore.")
    exit()

logging.info("caricata token.")

try:
    chatidFile = open(chatidpath,'r')
    CHATID = chatidFile.read().strip()
    chatidFile.close()
except IOError: 
    logging.error("Non ho trovato il file di chatid. E' necessario creare un file 'BotAssistant.chatid' con la chatidi telegram per il bot. In ogni caso questo file NON deve essere tracciato da git - viene ignorato perche' menzionato nel .gitignore.")
    exit()

logging.info("caricata chatid.")

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

GATEWAY = mysensors.SerialGateway('/dev/ttyMySensorsGateway', MySensorEvent, True)
GATEWAY.start()


# generate a name for this maggiordomo if does not exist
try:
    MaggiordomoIDFile = open(IDpath,'r')
    MaggiordomoID = MaggiordomoIDFile.read().strip()
    MaggiordomoIDFile.close()
#    bot.sendMessage(CHATID, "sono "+MaggiordomoID+". Mi sono appena svegliato")

except IOError: 
    logging.error("Non ho trovato il file con ID del maggiordomo. Genero ID e lo salvo")
    MaggiordomoID = "Maggiordomo-"+''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(10)) #da generare in modo random
    MaggiordomoIDFile = open(IDpath,'w')
    MaggiordomoIDFile.write(MaggiordomoID)
    MaggiordomoIDFile.close()

#    bot.sendMessage(CHATID,"sono "+MaggiordomoID+". Sono stato appena generato")

bot.sendMessage(CHATID,"Sono "+MaggiordomoID+". Inizio il monitoraggio dell'antifurto")

# Keep the program running.
while 1:
    time.sleep(1)
