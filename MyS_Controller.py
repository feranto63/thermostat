#!/usr/bin/python
#coding: utf-8

import logging
logging.basicConfig(level=logging.DEBUG)
_LOGGER = logging.getLogger(__name__)

import telepot.api

# DEFINIZIONE VARIABILI DI PERSONALIZZAZIONE
import sys

#PROPRIETARIO = sys.argv[1]  # get user from command-line
owner_found = False


import configparser as ConfigParser
#from backports import configparser as ConfigParser

settings = ConfigParser.ConfigParser()
settings.read('thermogram2.ini')
HEAT_ID = settings.getint('SectionOne','HEAT_ID')
HEATPUMP_ID = settings.getint('SectionOne','HEATPUMP_ID')

# HEAT_ID = 31

GATE_PRESENT = settings.getboolean('SectionOne','GATE_PRESENT')
try:
    GATE_ID = settings.getint('SectionOne','GATE_ID') # 0=relay on board; <int> = relay sensor ID
except:
    GATE_ID = 0

NUM_SENSORI = settings.getint('SectionOne','NUM_SENSORI')


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


				
def save_sensorlog(filename, t_stamp, temp, humidity, battery):
    filesensor = open(filename,"w")  #apre il file di log del sensore in write mode, se il file non esiste lo crea
    #####   print (( 'Temp={0:0.1f}*C  Humidity={1:0.1f}%'.format(temperature, humidity)))
    filesensor.write(t_stamp +" "+str(temp)+" "+str(humidity)+" "+str(battery))
    filesensor.close()  #chiude il file dei dati e lo salva

    
############## gestione dell'apertura del cancello con relay radio ##################
def OpenGate(gateID):
    
    orario = time.localtime(time.time())
    localtime = time.strftime("%Y-%m-%d %H:%M:%S", orario)
    ora_minuti = time.strftime("%H:%M", orario)
    
    GATEWAY.set_child_value(gateID, 1, 2, 0) #, ack=1)
    time.sleep(1)
    GATEWAY.set_child_value(gateID, 1, 2, 1) #, ack=1)

    f = open("gate_toggle","w")
    f.write(" ")
    f.close()  #chiude il file dei dati e lo salva
    print('eseguita apertura cancello')
   
    return()


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

sensor = [['2000-01-01 00:00:00',0.0, 0.0, 0.0] for x in range (300)]

	######### lettura sensori di temperatura #################

def read_sensors():
    global sensor, NUM_SENSORI
    for i in range (NUM_SENSORI):
        try:
            f = open("sensor"+str(i)+".log","r")  #apre il file dei dati in read mode
            value = f.read().split()  #legge la info del sensore sul file e divide per data, ora e valore
            f.close()  #chiude il file dei dati e lo salva
            sensor[i][0]= "%s" % str(value[0]) + " %s" % str(value[1])
            sensor[i][1]= "%.1f" % float(value[2])
            try:
                sensor[i][2]= "%.1f" % float(value[3])
            except:
                sensor[i][2]= 0.0
            try:
                sensor[i][3]= "%.1f" % float(value[4])
            except:
                sensor[i][3]= 0.0
        except IOError:
            sensor[i][1] = -99  #se il file non e' presente imposto il sensore a -99


######### FINE lettura sensori di temperatura ###########




def MySensorEvent(message):
    global MOVING_STATUS, ALARM_STATUS, ALARM_ACTIVE, sensor, MaggiordomoID, how_many_at_home
    """Callback for mysensors updates."""

    orario = time.localtime(time.time())
    #localtime = time.asctime( orario )
    localtime = time.strftime("%Y-%m-%d %H:%M:%S", orario)
    ora_minuti = time.strftime("%H:%M", orario)
	
#    print("sto per maneggiare un messaggio")
#    print("sensor_update " + str(message.node_id))
#    print("message.type " + str(message.type))
#    print("message.sub_type: "+str(message.sub_type))
#    print("message.payload: "+message.payload)
	
    PAYLOAD = message.payload
#
# CODICI NODE_ID
# 30 STATO ALLARME
# 32 SENSORE DI PRESENZA
# 37 SPIA ALLARME INSERITO
#

    if message.node_id == 30: # STATO ALLARME
#        print("message.node_id == 30")
        if message.child_id == 1: # sensore allarme
            if message.sub_type == 16:
#                print("message.sub_type == 16")
#                print("PAYLOAD = "+str(PAYLOAD))
                if int(PAYLOAD) == ALARM_STATUS:
#                    print("message.payload == "+str(ALARM_STATUS))
                    return()
                else:
                    ALARM_STATUS = int(PAYLOAD)
                    if int(PAYLOAD) == 0:
 #                       print("PAYLOAD == 0")
                        try:
                            bot.sendMessage(CHATID,"Sono "+MaggiordomoID+". E' scattato l'antifurto alle "+localtime)
                        except:
                            bot.sendMessage(CHATID,".Sono "+MaggiordomoID+". E' scattato l'antifurto alle "+localtime)
                    else:
  #                      print("PAYLOAD == 1")
                        try:
                            bot.sendMessage(CHATID,"Sono "+MaggiordomoID+". L'antifurto si e' spento alle "+localtime)
                        except:
                            bot.sendMessage(CHATID,".Sono "+MaggiordomoID+". L'antifurto si e' spento alle "+localtime)
        elif message.child_id == 2: # led allarme attivato
            if message.sub_type == 16:
                if int(PAYLOAD) == ALARM_ACTIVE:
#                    print("message.payload == "+str(ALARM_STATUS))
                    return()
                else:
                    ALARM_ACTIVE = int(PAYLOAD)
                    if int(PAYLOAD) == 0:  # ALLARME INSERITO
 #                       print("PAYLOAD == 0")
                        try:
                            bot.sendMessage(CHATID,"Sono "+MaggiordomoID+". E' stato attivato l'antifurto alle "+localtime, disable_notification=True)
                        except:
                            bot.sendMessage(CHATID,".Sono "+MaggiordomoID+". E' stato attivato l'antifurto alle "+localtime, disable_notification=True)
                        # invia messaggio di allarme inserito
                        GATEWAY.set_child_value(37, 1, 2, 1)

                    else:                  # ALLARME DISINSERITO
  #                      print("PAYLOAD == 1")
                        try:
                            bot.sendMessage(CHATID,"Sono "+MaggiordomoID+". E' stato disattivato l'antifurto alle "+localtime, disable_notification=True)
                        except:
                            bot.sendMessage(CHATID,".Sono "+MaggiordomoID+". E' stato disattivato l'antifurto alle "+localtime, disable_notification=True)
                        #invia messaggio di allarme disinserito
                        GATEWAY.set_child_value(37, 1, 2, 0)
           
    elif message.node_id == 32: # SENSORE DI PRESENZA
        print("message.node_id == 32")
        if message.sub_type == 16:
            print("message.sub_type == 16")
            print("PAYLOAD = "+str(PAYLOAD))
            if int(PAYLOAD) == MOVING_STATUS:
                print("message.payload == "+str(MOVING_STATUS))
                return()
            else:
                MOVING_STATUS = int(PAYLOAD)
                if int(PAYLOAD) == 1:
                    print("PAYLOAD == 1")
#                    if how_many_at_home == 0:
                    if ALARM_ACTIVE == 0:
                        try:
                            bot.sendMessage(CHATID,"Sono "+MaggiordomoID+". Ho notato un movimento alle "+localtime, disable_notification=True)
                        except:
                            bot.sendMessage(CHATID,".Sono "+MaggiordomoID+". Ho notato un movimento alle "+localtime, disable_notification=True)
                else:
                    print("PAYLOAD == 0")
                    #try:
                    #    bot.sendMessage(CHATID,"Sono "+MaggiordomoID+". Non c'e' piu' movimento alle "+localtime)
                    #except:
                    #    bot.sendMessage(CHATID,".Sono "+MaggiordomoID+". Non c'e' piu' movimento alle "+localtime)
    else:
 #       print("node_id="+str(message.node_id))
        if  int(message.type) == 1:  # is a SET message
            if int(message.sub_type) == 0: #it is a temperature
                sensor[message.node_id][1] = float(PAYLOAD)
                sensor[message.node_id][0] = localtime
 #               print("it's temperature")
            elif int(message.sub_type) == 1: # it is a humidity
                    sensor[message.node_id][2] = float(PAYLOAD)
                    sensor[message.node_id][0] = localtime
 #                   print("it's humidity")
            elif int(message.sub_type) == 2: # it is a V_STATUS
                    sensor[message.node_id][2] = float(PAYLOAD)
                    sensor[message.node_id][0] = localtime
 #                   print("it's V_STATUS")

        elif int(message.type) == 3: # is an INTERNAL message
#            print("ho trovato un internal message")
            if int(message.sub_type) == 0: # it's a battery level
#                print("trovato battery level")
                sensor[message.node_id][3] = int(PAYLOAD)
#                print("memorizzato valore battery level")
                sensor[message.node_id][0] = localtime
#                print("it's battery level")
            else:
                print("internal message sconosciuto:"+str(message.sub_type))
                
#        print("test")
        sensorfilename = "sensor"+str(message.node_id)+".log"
        
        if MaggiordomoID == "Battista":
            if message.node_id == 8: #soggiorno
                sensorfilename = "sensor1.log"
            elif message.node_id == 31: #giardino
                sensorfilename = "sensor2.log"
            else:
                sensorfilename = "sensor"+str(message.node_id)+".log"
        elif MaggiordomoID == "Ursula":
            if message.node_id == 15: #zona notte
                sensorfilename = "sensor1.log"
            else:
                sensorfilename = "sensor"+str(message.node_id)+".log"
        elif MaggiordomoID == "Ambrogio":
            if message.node_id == 5: #giardino
                sensorfilename = "sensor1.log"
            elif message.node_id == 4: #zona notte
                sensorfilename = "sensor2.log"
            elif message.node_id == 10: # cucina
                sensorfilename = "sensor3.log"
            elif message.node_id == 34: # sala hobby
                sensorfilename = "sensor4.log"
            elif message.node_id == 39: # cameretta
                sensorfilename = "sensor5.log"
        elif MaggiordomoID == "Sas":
            if message.node_id == 37: #zona notte
                sensorfilename = "sensor1.log"
        elif MaggiordomoID == "Verrecchie":
            if message.node_id == 34: #giardino/balcone
                sensorfilename = "sensor1.log"

        else:
            sensorfilename = "sensor"+str(message.node_id)+".log"

        sensor[message.node_id][3] = GATEWAY.sensors[message.node_id].battery_level
#        print("sensorfilename ="+sensorfilename)
#        print("timestamp="+sensor[message.node_id][0])
#        print("temp="+str(sensor[message.node_id][1]))
#        print("Humidity="+str(sensor[message.node_id][2]))
#        print("Battery="+str(sensor[message.node_id][3]))

        save_sensorlog(sensorfilename, sensor[message.node_id][0], sensor[message.node_id][1], sensor[message.node_id][2], sensor[message.node_id][3])
    return()

######## legge da file lo stato del cancello ###########
def read_gate_status():
	try:
		f = open("gate_toggle","r")  #apre il file dei dati in read mode
		g_status=f.read().strip()   #legge la info di presence sul file
		f.close()  #chiude il file dei dati e lo salva
		if g_status == "0":
			gate_status = True
		else:
			gate_status = False
	except IOError:
		gate_status = False  #se il file non e' presente imposto la presence a False
	return(gate_status)


######## legge da file lo stato del riscaldamento e dello standby ###########
def read_heating_status():
	try:
		f = open("heat_toggle","r")  #apre il file dei dati in read mode
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

######## legge da file lo stato della pompa di calore ###########
def read_heatpump_status():
	try:
		f = open("heatpump_toggle","r")  #apre il file dei dati in read mode
		h_status=f.read().strip()   #legge la info di presence sul file
		f.close()  #chiude il file dei dati e lo salva
		if h_status == "ON":
			heatpump_status = True
		else:
			heatpump_status = False
	except IOError:
		heatpump_status = False  #se il file non e' presente imposto la presence a False
	return(heatpump_status)

#################### accende o spegne i termosifoni #############
def TurnON_termosifoni(heatID):
    
    orario = time.localtime(time.time())
    localtime = time.strftime("%Y-%m-%d %H:%M:%S", orario)
    ora_minuti = time.strftime("%H:%M", orario)
    
    retries = 4
    while retries > 0:
        GATEWAY.set_child_value(heatID, 1, 2, 0) #, ack=1)
#        GATEWAY.set_child_value(heatID, 1, 2, msg_type=2, ack=1)
        time.sleep(5)
        try:
            values = GATEWAY.sensors[heatID].children[1].values[2]
        except:
            print("errore di lettura dello stato del relay")
            retries = 0
            return()
        print("rilettura stato relay:"+values)
        if int(values) == 0:
            retries = 0
            return()
        else:
            retries = retries-1
    try:
        bot.sendMessage(CHATID,"Sono "+MaggiordomoID+". Non sono riuscito ad accendere i termosifoni alle "+localtime, disable_notification=True)
    except:
        bot.sendMessage(CHATID,".Sono "+MaggiordomoID+". Non sono riuscito ad accendere i termosifoni alle "+localtime, disable_notification=True)
    
    return()

def TurnOFF_termosifoni(heatID):
    orario = time.localtime(time.time())
    localtime = time.strftime("%Y-%m-%d %H:%M:%S", orario)
    ora_minuti = time.strftime("%H:%M", orario)
    
    retries = 4
    while retries > 0:

        GATEWAY.set_child_value(heatID, 1, 2, 1) #, ack=1)
#        GATEWAY.set_child_value(heatID, 1, 2, msg_type=2, ack=1)
        time.sleep(5)
        try:
            values = GATEWAY.sensors[heatID].children[1].values[2]
        except:
            print("errore di lettura dello stato del relay")
            retries = 0
            return()
        print("rilettura stato relay:"+values)
        if int(values) == 1:
            retries = 0
            return()
        else:
            retries = retries-1
    try:
        bot.sendMessage(CHATID,"Sono "+MaggiordomoID+". Non sono riuscito a spegnere i termosifoni alle "+localtime, disable_notification=True)
    except:
        bot.sendMessage(CHATID,".Sono "+MaggiordomoID+". Non sono riuscito a spegnere i termosifoni alle "+localtime, disable_notification=True)

    return()

#################### accende o spegne la pompa di calore #############
def TurnON_heatpump(heatID):
    
    orario = time.localtime(time.time())
    localtime = time.strftime("%Y-%m-%d %H:%M:%S", orario)
    ora_minuti = time.strftime("%H:%M", orario)
    
    retries = 4
    while retries > 0:
        GATEWAY.set_child_value(heatID, 1, 2, 1) #, ack=1)
#        GATEWAY.set_child_value(heatID, 1, 2, msg_type=2, ack=1)
        time.sleep(5)
        try:
            values = GATEWAY.sensors[heatID].children[1].values[2]
        except:
            print("errore di lettura dello stato della pompa di calore")
            retries = 0
            return()
        print("rilettura stato pompa di calore:"+values)
        if int(values) == 1:
            retries = 0
            return()
        else:
            retries = retries-1
    try:
        bot.sendMessage(CHATID,"Sono "+MaggiordomoID+". Non sono riuscito ad accendere la pompa di calore alle "+localtime, disable_notification=True)
    except:
        bot.sendMessage(CHATID,".Sono "+MaggiordomoID+". Non sono riuscito ad accendere la pompa di calore alle "+localtime, disable_notification=True)
    
    return()

def TurnOFF_heatpump(heatID):
    orario = time.localtime(time.time())
    localtime = time.strftime("%Y-%m-%d %H:%M:%S", orario)
    ora_minuti = time.strftime("%H:%M", orario)
    
    retries = 4
    while retries > 0:

        GATEWAY.set_child_value(heatID, 1, 2, 0) #, ack=1)
#        GATEWAY.set_child_value(heatID, 1, 2, msg_type=2, ack=1)
        time.sleep(5)
        try:
            values = GATEWAY.sensors[heatID].children[1].values[2]
        except:
            print("errore di lettura dello stato della pompa di calore")
            retries = 0
            return()
        print("rilettura stato pompa di calore:"+values)
        if int(values) == 0:
            retries = 0
            return()
        else:
            retries = retries-1
    try:
        bot.sendMessage(CHATID,"Sono "+MaggiordomoID+". Non sono riuscito a spegnere la pompa di calore alle "+localtime, disable_notification=True)
    except:
        bot.sendMessage(CHATID,".Sono "+MaggiordomoID+". Non sono riuscito a spegnere la pompa di calore alle "+localtime, disable_notification=True)

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
mylocalIPaddress = str(subprocess.check_output(['hostname','-I']))
print('myIPaddress:'+myIPaddress+" "+mylocalIPaddress)


import mysensors.mysensors as mysensors

'''
Message
    gateway - the gateway instance
    node_id - the sensor node identifier
    child_id - the child sensor id
    type - the message type (int)
    ack - True is message was an ACK, false otherwise
    sub_type - the message sub_type (int)
    payload - the payload of the message (string)

SerialGateway/TCPGateway/MQTTGateway
    sensors - a dict containing all nodes for the gateway; node is of type Sensor

Sensor - a sensor node
    children - a dict containing all child sensors for the node
    sensor_id - node id on the MySensors network
    type - 17 for node or 18 for repeater
    sketch_name
    sketch_version
    battery_level
    protocol_version - the mysensors protocol version used by the node

ChildSensor - a child sensor
    id - Child id on the parent node
    type - Data type, S_HUM, S_TEMP etc.
    values - a dictionary of values (V_HUM, V_TEMP, etc.)
    
Getting the type and values of node 23, child sensor 4 would be performed as follows:

s_type = GATEWAY.sensors[23].children[4].type
values = GATEWAY.sensors[23].children[4].values
'''

ALARM_STATUS = 1
ALARM_ACTIVE = 1
MOVING_STATUS = 1

#GATEWAY = mysensors.SerialGateway('/dev/ttyMySensorsGateway', MySensorEvent, persistence=False)
GATEWAY = mysensors.SerialGateway('/dev/ttyMySensorsGateway', baud=115200, event_callback=MySensorEvent, persistence=True,
  persistence_file='/home/pi/git/thermostat/thermostat/mysensors.pickle', protocol_version='2.0')

GATEWAY.start_persistence()
_LOGGER.debug("Starting Gateway")
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

bot.sendMessage(CHATID,"Sono "+MaggiordomoID+". Inizio il monitoraggio dei sensori wireless e dell'antifurto", disable_notification=True)

HEAT_STATUS = read_heating_status()

if HEAT_STATUS:
	print("initial heat status ON")
else:
	print("initial heat status OFF")


#restore accensione riscaldamento
if HEAT_STATUS:
	TurnON_termosifoni(HEAT_ID)
else:
	TurnOFF_termosifoni(HEAT_ID)

HEATPUMP_STATUS = read_heatpump_status()

if HEATPUMP_STATUS:
	print("initial heatpump status ON")
else:
	print("initial heatpump status OFF")


#restore accensione pompa di calore
if HEATPUMP_STATUS:
	TurnON_heatpump(HEATPUMP_ID)
else:
	TurnOFF_heatpump(HEATPUMP_ID)

    
# read stored values of sensors
read_sensors()


CHECK_INTERVAL = 15*60 # every 15 minutes (in seconds)

now = time.time()
check_timer = now + CHECK_INTERVAL  #inizializza check_timer

# Keep the program running.
while True:
    CURRENT_HEAT=read_heating_status()
    if CURRENT_HEAT != HEAT_STATUS:
        if CURRENT_HEAT:
            TurnON_termosifoni(HEAT_ID)
        else:
            TurnOFF_termosifoni(HEAT_ID)
        HEAT_STATUS = CURRENT_HEAT

    CURRENT_HEATPUMP=read_heatpump_status()
    if CURRENT_HEATPUMP != HEATPUMP_STATUS:
        if CURRENT_HEATPUMP:
            TurnON_heatpump(HEATPUMP_ID)
        else:
            TurnOFF_heatpump(HEATPUMP_ID)
        HEATPUMP_STATUS = CURRENT_HEATPUMP

    # calcola chi e' a casa
    # legge su file quante persone sono a casa per MySController
    try:
        f = open("how_many_at_home","r")
        how_many_at_home=int(f.read())
        f.close()  #chiude il file dei dati e lo salva
    except:
        how_many_home=0
	
    now = time.time()
    if now > check_timer:
        # verifica lo stato del relay e nel caso lo resetta
        try:
            values = GATEWAY.sensors[HEAT_ID].children[1].values[2]
        except:
            values = 99
        if int(values) == 1:
            relay_status = 'OFF'
        elif int(values) == 0:
            relay_status = 'ON'
        else:
            print ("errore di lettura dello stato del relay:"+str(values))
            relay_status = HEAT_STATUS
        if relay_status != HEAT_STATUS:
            if HEAT_STATUS:
                TurnON_termosifoni(HEAT_ID)
            else:
                TurnOFF_termosifoni(HEAT_ID)

        check_timer = now + CHECK_INTERVAL  #inizializza check_timer
    
    if read_gate_status():
        OpenGate(GATE_ID)
    
    time.sleep(5)
