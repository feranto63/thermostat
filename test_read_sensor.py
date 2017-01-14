#!/usr/bin/python
#coding: utf-8

import telepot.api
import urllib3

# posto retry = 3 per evitare exception sul send.message casuale
telepot.api._pools = {
    'default': urllib3.PoolManager(num_pools=3, maxsize=10, retries=3, timeout=30),
}

# DEFINIZIONE VARIABILI DI PERSONALIZZAZIONE
import sys

#PROPRIETARIO = sys.argv[1]  # get user from command-line
owner_found = False


import configparser as ConfigParser

settings = ConfigParser.ConfigParser()
settings.read('thermogram2.ini')
nome_maggiordomo = settings.get('SectionOne','nome_maggiordomo')
male_maggiordomo = settings.getboolean('SectionOne','male_maggiordomo')
persone_della_casa = settings.getint('SectionOne','persone_della_casa')
persona= settings.get('SectionOne','persona').split("\n")
#persona_at_home=settings.getboolean('SectionOne','persona_at_home').split("\n")
persona_at_home=[True, True, True, True, True, True, True, True, True]
persona_retry=[0,0,0,0,0,0,0,0,0]
imap_host = settings.get('SectionOne','imap_host')
EMAIL_ID=settings.get('SectionOne','EMAIL_ID')
EMAIL_PASSWD=settings.get('SectionOne','EMAIL_PASSWD')
persona_IP=settings.get('SectionOne','persona_IP').split("\n")
persona_BT=settings.get('SectionOne','persona_BT').split("\n")
persona_WIFI=settings.get('SectionOne','persona_WIFI').split("\n")
persona_ARP=settings.get('SectionOne','persona_ARP').split("\n")
GATE_PRESENT = settings.getboolean('SectionOne','GATE_PRESENT')
SECONDARY_HEAT = settings.getboolean('SectionOne','SECONDARY_HEAT') #indica se e' presente la fonte di riscaldamento secondaria
IP_PRESENCE = settings.getboolean('SectionOne','IP_PRESENCE')
BT_PRESENCE = settings.getboolean('SectionOne','BT_PRESENCE')
ARP_PRESENCE = settings.getboolean('SectionOne','ARP_PRESENCE')
PRESENCE_MAC = settings.getboolean('SectionOne','PRESENCE_MAC')  #indica se se la presenza e' su base WiFi MAC Address
DHT_PRESENCE = settings.getboolean('SectionOne','DHT_PRESENCE') #indica se e' presente il sensore DHT
DHT_TYPE = settings.getint('SectionOne','DHT_TYPE')
DS_PRESENCE = settings.getboolean('SectionOne','DS_PRESENCE') # indica se e' presente il sensore di temperatura 18DS20
PRESENCE_RETRY = settings.getint('SectionOne','TIMEOUT')
owner_found= settings.getboolean('SectionOne','owner_found')


if not owner_found:
    sys.exit("owner not found")

for n in range(persone_della_casa):
    print (persona[n]+" - "+persona_ARP[n]+"\n")

FILESCHEDULE="fileschedule"
FILEHEATING="fileheating"
HEAT_ON  = 0
HEAT_OFF = 1
HEAT_PIN = 17   # GPIO della caldaia (heating principale)
HEAT2_PIN = 27  # GPIO della stufa (heating secondario)
GATE_PIN = 22
GATE_ON = 0
GATE_OFF = 1
DHT_PIN = 18
dbname='/var/www/templog.db'
hide_notify = False
debug_notify = True

week_name=['DOM','LUN','MAR','MER','GIO','VEN','SAB'] #domenica = 0
DELTA_TEMP = 0.2

overwrite_duration = 1000 #ore di attivazione dell'overwrite; se = 1000 è permanente
overwrite_temp = 25 #temperatura in gradi di funzionamento in overwrite da settare sia per /turnon che per /turnoff


MAIN_HEAT = [1,1,1,1,1,1,1,1,1,1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]  # indica se usare la caldaia principale nell'ora x
#           [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23]

lucchetto_chiuso = '\U0001f512' # '\xF0\x9F\x94\x92'  #	lock U+1F512
lucchetto_aperto = '\U0001f513' # '\xF0\x9F\x94\x93'  #    open lock U+1F513	


#imports for thermometer reading
import os
import glob
import time
#imports for gmail reading
import imaplib
import email
#import for Telegram API
# import pprint
import telepot

# import requests

import bluetooth

#import library for logging
import logging
logging.basicConfig(
        filename='termostato.log',
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.WARN)


###################### database per la memorizzazione delle temperature ###############
import sqlite3

# store the temperature in the database
def log_temperature(orario,temp, tempDHT, humidity, ExtTemp, HeatOn, TargetTemp):

    conn=sqlite3.connect(dbname)
    curs=conn.cursor()
    dati_da_inserire = [orario,temp,tempDHT,humidity, ExtTemp, HeatOn, TargetTemp]
    curs.execute("INSERT INTO temps values (?,?,?,?,?,?,?)", dati_da_inserire)
    # commit the changes
    conn.commit()
    conn.close()

# store the presence in the database
def log_presence(orario, nome, verso):

    conn=sqlite3.connect(dbname)
    curs=conn.cursor()
    dati_da_inserire = [orario, nome, verso]
    curs.execute("INSERT INTO presence values (?,?,?)", dati_da_inserire)
    # commit the changes
    conn.commit()

    with conn:

        curs = conn.cursor()    
        if verso=="IN":
            incasa = True
        else:
            incasa = False
        dati_da_inserire = [nome, incasa, orario]
        dati_da_aggiornare = [orario, incasa, nome]
        curs.execute("SELECT * FROM persona WHERE nome = ?",(nome,))
        rows = curs.fetchone()
        if rows == None:
            curs.execute("INSERT INTO persona values (?,?,?)", dati_da_inserire)        
        else:
            curs.execute("UPDATE persona SET timestamp=?, incasa=? WHERE nome=?", dati_da_aggiornare)        
        conn.commit()
    conn.close()

################### gestione cronotermostato ###########################
import calendar

#import thermoschedule
# schedulazione della programmazione della temperatura
#mySchedule is a matrix [7 x 24] [lunedi' is first row]
mySchedule = [['17' for x in range(24)] for x in range(7)] 

def initialize_schedule():
    global mySchedule, FILESCHEDULE
    try:
        fileschedule = open(FILESCHEDULE,"r")  #apre il file dei dati in append mode, se il file non esiste lo crea
        for i in range (0,7):
            tmpstr=fileschedule.readline().strip(";\n")
            mySchedule[i]=tmpstr.split(";")  #scrive la info di presence ed il timestam sul file
        fileschedule.close()  #chiude il file dei dati e lo salva
    except IOError:
        mySchedule= [['17','17','17','17','17','17','20','20','20','18','18','18','18','20','20','18','18','18','18','18','20','20','20','17'],
                    ['17','17','17','17','17','17','20','20','20','18','18','18','18','20','20','18','18','18','18','18','20','20','20','17'],
                    ['17','17','17','17','17','17','20','20','20','18','18','18','18','20','20','18','18','18','18','18','20','20','20','17'],
                    ['17','17','17','17','17','17','20','20','20','18','18','18','18','20','20','18','18','18','18','18','20','20','20','17'],
                    ['17','17','17','17','17','17','20','20','20','18','18','18','18','20','20','18','18','18','18','18','20','20','20','17'],
                    ['17','17','17','17','17','17','20','20','20','18','18','18','18','20','20','18','18','18','18','18','20','20','20','17'],
                    ['17','17','17','17','17','17','17','17','20','20','18','18','18','20','20','20','18','18','18','18','20','20','20','17'],
                    ['17','17','17','17','17','17','17','17','20','20','18','18','18','20','20','20','18','18','18','18','20','20','20','17']]

def current_target_temp():
    global mySchedule
    
    now = time.time()
    orario = time.localtime(now)

    curr_hour=int(time.strftime("%H",orario))

    localtime = time.asctime( orario )
    day_of_week= int(time.strftime("%w", orario))

    target_temp=mySchedule[day_of_week][curr_hour]
    return(float(target_temp))

                     
def save_schedule():
    global mySchedule, FILESCHEDULE
    
    fileschedule = open(FILESCHEDULE,"w")  #apre il file dei dati in append mode, se il file non esiste lo crea
    for i in range (0,7):
        for y in range (0,24):
            fileschedule.write(mySchedule[i][y]+";")
        fileschedule.write("\n")#scrive la info di presence ed il timestam sul file
    fileschedule.close()  #chiude il file dei dati e lo salva

    
# read the comfort temperature table to database
def get_tempschedule():
    global mySchedule, week_name, dbname
    conn=sqlite3.connect(dbname)
    curs=conn.cursor()
    curs.execute("SELECT * FROM tempschedule")
    for i in range (7):
        data=curs.fetchone()
        day_index=week_name.index(data[0])
        for j in range (24):
            mySchedule[day_index][j]=data[j+1]
    conn.close()

# write the modified comfort temperature table to database
def put_tempschedule(giorno_attuale, ora_attuale, nuova_temp):
    global mySchedule, week_name, dbname

    nuova_temp=round(nuova_temp,1)
    day_index = week_name[giorno_attuale]
    if ora_attuale < 10:
        column_name = "h0"+str(ora_attuale)
    else:
        column_name = "h"+str(ora_attuale)
    conn=sqlite3.connect(dbname)
    curs=conn.cursor()
    command="UPDATE tempschedule SET "+column_name+" = ? WHERE giorno = ?"
    curs.execute(command, [nuova_temp, day_index])
    conn.commit()
    conn.close()
    mySchedule[giorno_attuale][ora_attuale]=nuova_temp

################### fine gestione cronotermostato ######################

def isnumeric(s):
    try:
        i = float(s)
        return True
    except (ValueError, TypeError):
        return False


# definisce la variabile per la conferma dell'apertura del cancello
opengate_confirming = False
