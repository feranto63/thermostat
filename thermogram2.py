#!/usr/bin/env python3.6
#coding: utf-8

import telepot.api
import urllib3
import subprocess


# posto retry = 3 per evitare exception sul send.message casuale
telepot.api._pools = {
    'default': urllib3.PoolManager(num_pools=3, maxsize=10, retries=3, timeout=30),
}

# DEFINIZIONE VARIABILI DI PERSONALIZZAZIONE
import sys

#PROPRIETARIO = sys.argv[1]  # get user from command-line
owner_found = False


from backports import configparser as ConfigParser
# import configparser as ConfigParser

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

try:
    NOTIFY_PRESENCE=settings.getboolean('SectionOne','NOTIFY_PRESENCE')
except:
    NOTIFY_PRESENCE=True
    
GATE_PRESENT = settings.getboolean('SectionOne','GATE_PRESENT')
try:
    GATE_ID = settings.getint('SectionOne','GATE_ID') # 0=relay on board; <int> = relay sensor ID
except:
    GATE_ID = 0

HEAT_ID = settings.getint('SectionOne','HEAT_ID') # 0=relay on board; <int> = relay sensor ID
HEATPUMP_ID = settings.getint('SectionOne','HEATPUMP_ID')
SECONDARY_HEAT = settings.getboolean('SectionOne','SECONDARY_HEAT') #indica se e' presente la fonte di riscaldamento secondaria
IP_PRESENCE = settings.getboolean('SectionOne','IP_PRESENCE')
BT_PRESENCE = settings.getboolean('SectionOne','BT_PRESENCE')
ARP_PRESENCE = settings.getboolean('SectionOne','ARP_PRESENCE')
PRESENCE_MAC = settings.getboolean('SectionOne','PRESENCE_MAC')  #indica se se la presenza e' su base WiFi MAC Address
DHT_PRESENCE = settings.getboolean('SectionOne','DHT_PRESENCE')  #indica se e' presente il sensore DHT
DHT_TYPE = settings.getint('SectionOne','DHT_TYPE')
DS_PRESENCE = settings.getboolean('SectionOne','DS_PRESENCE') # indica se e' presente il sensore di temperatura DS18B20 (family 24h)
DS1820_PRESENCE = settings.getboolean('SectionOne','DS1820_PRESENCE') # indica se e' presente il sensore di temperatura DS1820 (familiy 10h)
PRESENCE_RETRY = settings.getint('SectionOne','TIMEOUT')

NUM_SENSORI = settings.getint('SectionOne','NUM_SENSORI')
sensor_type = settings.get('SectionOne','sensor_type').split("\n")
# sensori = settings.get('SectionOne','sensori').split("\n")

TIPO_SENSORE = ['living','giardino','zona notte','cucina','bagno','sala hobby','cameretta']
# 0 = living
# 1 = giardino
# 2 = zona notte
# 3 = cucina
# 4 = bagno
# 5 = sala hobby
# 6 = cameretta

main_sensor = int(settings.get('SectionOne','main_sensor'))
sensor_value = [[' ',0.0, 0.0, 0.0],[' ',0.0, 0.0, 0.0],[' ',0.0, 0.0, 0.0],[' ',0.0, 0.0, 0.0],[' ',0.0, 0.0, 0.0],[' ',0.0, 0.0, 0.0],[' ', 0.0, 0.0, 0.0],[' ', 0.0, 0.0, 0.0],[' ', 0.0, 0.0, 0.0],[' ', 0.0, 0.0, 0.0],[' ', 0.0, 0.0, 0.0],[' ', 0.0, 0.0, 0.0],[' ', 0.0, 0.0, 0.0]] #time,temp,humid

owner_found= settings.getboolean('SectionOne','owner_found')

sensori = [' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ']
ExtTempID = -99 #indice del sensore della temperatura esterna, se -99 non c'e' sensore esterno altrimenti è l'indice del sensore esterno
for i in range (NUM_SENSORI):
    s_type = int(sensor_type[i])
    if s_type == 1: # giardino
        ExtTempID = i
    sensori[i] = TIPO_SENSORE[s_type]
    
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
GATE_PIN = 23 #GPIO del cancello
GATE_ON = 0
GATE_OFF = 1
DHT_PIN = 18
FILEHEATPUMP="fileheatpump"

dbname='/var/www/templog.db'
hide_notify = False
debug_notify = True

week_name=['DOM','LUN','MAR','MER','GIO','VEN','SAB'] #domenica = 0

DELTA_TEMP = 0.2

overwrite_duration = 1000 #ore di attivazione dell'overwrite; se = 1000 è permanente
overwrite_temp = 25 #temperatura in gradi di funzionamento in overwrite da settare sia per /turnon che per /turnoff


#MAIN_HEAT = [0,0,0,0,0,0,0,0,0,0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]  # indica se usare la caldaia principale nell'ora x
#MAIN_HEAT = [1,1,1,1,1,1,1,1,1,1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1]  # indica se usare la caldaia principale nell'ora x
MAIN_HEAT =  [1,1,1,1,1,1,1,1,1,1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]  # indica se usare la caldaia principale nell'ora x
#            [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23]
FORCE_HOUR = [1,1,1,1,1,1,1,1,1,1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1]  # indica se forzare la presenza

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



def parse_weekday(s):
    s = s.upper()
    if s in week_name:
        return week_name.index(s)

    try:
        i = int(s)
        if((i >= 0) and (i < 7)):
            return i
        else:
            return None
    except (ValueError,TypeError):
        return None


    
############## gestione dell'apertura del cancello con relay radio ##################
def setRadioGate(xID, gate_toggle):
    print('xID Gate ='+str(xID)+ 'gate_toggle: '+str(gate_toggle))
    if xID == 0:
        GPIO.output(GATE_PIN, GATE_ON) # apro il cancello
        time.sleep(2)
        GPIO.output(GATE_PIN, GATE_OFF) # reset apertura cancello
    else:
        f = open("gate_toggle","w")
        f.write(str(gate_toggle))
        f.close()  #chiude il file dei dati e lo salva
    print('eseguita apertura cancello')
    return()
######################################################################################

# definisce la variabile per la conferma dell'apertura del cancello
opengate_confirming = False

###################### gestisce i comandi inviati al Telegram Bot
def handle(msg):
    global persona_at_home
    global last_report, report_interval     #parametri per il monitoraggio su file delle temperature
    global heating_status, heating_standby, heating_overwrite  #stato di accensione dei termosifoni
    global who_is_at_home, how_many_at_home
    global mySchedule, CurTemp, CurTargetTemp, CurTempDHT, CurHumidity
    global CHAT_ID, GATE_PRESENT, GATE_PIN, GATE_ON, GATE_OFF
    global pulizie_status, pulizie_timer
    global opengate_confirming
    global main_show_keyboard
    global debug_notify
    global nome_maggiordomo, male_maggiordomo
    global overwrite_duration, overwrite_temp, overwrite_timer
    global sensor_value, sensor_type, sensori, NUM_SENSORI
    
    logging.debug('inizio la gestione di handle')
    msg_type, chat_type, chat_id = telepot.glance(msg)
    msg_sender = msg['from']['first_name']
    msg_username = msg['from']['username']
    
    # ignore non-text message
    if msg_type != 'text':
        return
    
    full_command = msg['text']
    command_list = full_command.split()
    num_args = len(command_list)
    if "@" in command_list[0]:    #command_list[>0] sono gli argomenti associati al comando
        main_command, bot_name = command_list[0].split("@")
    else:
        main_command = command_list[0]
        
    command = main_command.strip().lower()
    
    #CurTemp = read_temp()
    CurTargetTemp=current_target_temp()

    
    orario = time.localtime(time.time())
    localtime = time.asctime( orario )
    giorno_ora_minuti = time.strftime("%a %H:%M", orario)
    ora_attuale = int(time.strftime("%H", orario))
    giorno_attuale = int(time.strftime("%w", orario))
    
    if heating_status:
        heatstat = "acceso"
    else:
        heatstat = "spento"
    
    logging.debug('elaboro il comando '+command)
    
    if command == '/now':
        if heating_status:
            heatstat = "acceso"
        else:
            heatstat = "spento"
#        CurTempDHT, CurHumidity = read_TandH()
        if isnumeric(str(CurHumidity)):
            strCurHumidity = str("%0.1f" % CurHumidity)
        else:
            strCurHumidity = str(CurHumidity)
        if isnumeric(str(CurTempDHT)):
            strCurTempDHT = str("%0.1f" % CurTempDHT)
        else:
            strCurTempDHT= str(CurTempDHT)
        messaggio=""
        for i in range (NUM_SENSORI):
            messaggio+="La temperatura ("+sensori[i]+") e' di "+str("%0.1f" % float(sensor_value[i][1]))+" C\n"
        messaggio+="L'umidita' misurata e' di "+strCurHumidity+"%\n"
        messaggio+="La temperatura di comfort e' di "+str(CurTargetTemp)+" C\n"
        messaggio+="Il riscaldamento e' "
        if pulizie_status:
            messaggio+="disattivato per pulizie"
        else:
            messaggio+=heatstat
            if heating_overwrite:
                messaggio+=" per overwrite"
        bot.sendMessage(CHAT_ID, messaggio, disable_notification=debug_notify)
    elif command == '/annulla':
        heating_overwrite = False
        bot.sendMessage(CHAT_ID, "Annullo overwrite",disable_notification=True)
    elif command == '/ho_freddo':

        bot.sendMessage(CHAT_ID, "Ho capito che hai freddo", disable_notification=debug_notify)
        f = open("heating_update","a")
        f.write("F,"+heatstat+","+giorno_ora_minuti+","+str("%0.1f" % CurTemp)+","+str(CurTargetTemp)+"\n")
        f.close()  #chiude il file dei dati e lo salva
        # modifica la temperatura di comfort
        put_tempschedule(int(giorno_attuale),int(ora_attuale),float(CurTargetTemp+DELTA_TEMP))
        bot.sendMessage(CHAT_ID, "Nuova temperatura di comfort per il giorno "+week_name[giorno_attuale]+" ora "+str(ora_attuale)+"="+str("%0.1f" % (CurTargetTemp+DELTA_TEMP)), disable_notification=debug_notify)
    elif command == '/ho_caldo':
        bot.sendMessage(CHAT_ID, "Ho capito che hai caldo", disable_notification=debug_notify)
        f = open("heating_update","a")
        f.write("C,"+heatstat+","+giorno_ora_minuti+","+str("%0.1f" % CurTemp)+","+str(CurTargetTemp)+"\n")
        f.close()  #chiude il file dei dati e lo salva
        # modifica la temperatura di comfort
        put_tempschedule(int(giorno_attuale),int(ora_attuale),float(CurTargetTemp-DELTA_TEMP))
        bot.sendMessage(CHAT_ID, "Nuova temperatura di comfort per il giorno "+week_name[giorno_attuale]+" ora "+str(ora_attuale)+"="+str("%0.1f" % (CurTargetTemp-DELTA_TEMP)), disable_notification=debug_notify)


    elif command == '/set':
        if len(command_list) in [3,4]:
            if (len(command_list) == 3):
                time_to_set = int(command_list[1])
                temp_to_set = float(command_list[2])
                days_to_set = range(7)
            else:
                days_to_set = [ parse_weekday(command_list[1]) , ]
                time_to_set = int(command_list[2])
                temp_to_set = float(command_list[3])

            if days_to_set[0] is None:
                bot.sendMessage(CHAT_ID, "Errore: giorno settimana non valido.")
                days_to_set = []
                days_to_set_names = "NONE"
            else:
                days_to_set_names = ", ".join([week_name[d] for d in days_to_set ] )

            bot.sendMessage(CHAT_ID,"Imposto temperatura %0.1f C per ora %d nei giorni: %s."%(temp_to_set,time_to_set, days_to_set_names))

            for giorno in days_to_set:
                put_tempschedule(giorno, int(time_to_set), float(temp_to_set))

        else:
            bot.sendMessage(CHAT_ID,"Errore: numero argomenti non valido.")

    elif command == "/table":
        get_tempschedule()
        outstring = ".\t"+ "\t".join(week_name) + "\n"
        for hour in range(24):
            outstring+= str(hour)+":00|\t"
            for day in range(7):
                outstring += "%0.1f\t"%(mySchedule[day][hour])
            outstring+="\n"
            
        bot.sendMessage(CHAT_ID, outstring)


		

    elif command == '/casa':
        who_is_at_home=""
        how_many_at_home=0
        for who_at_home in range(persone_della_casa):
            if persona_at_home[who_at_home]:
                who_is_at_home=who_is_at_home+persona[who_at_home]+" "
                how_many_at_home=how_many_at_home+1
        if how_many_at_home != 0:
            if how_many_at_home == 1:
                bot.sendMessage(CHAT_ID, who_is_at_home+"e' a casa", disable_notification=debug_notify)
            else:
                bot.sendMessage(CHAT_ID, who_is_at_home+"sono a casa", disable_notification=debug_notify)
        else:
            if male_maggiordomo:
                sex_indicator = "o"
            else:
                sex_indicator = "a"
            who_is_at_home = nome_maggiordomo+" e' sol"+sex_indicator+" a casa, Padrone"
            bot.sendMessage(CHAT_ID, who_is_at_home, disable_notification=debug_notify)
    elif command == '/help':
        # send message for help
        messaggio="il mio nome e' "+nome_maggiordomo+" e custodisco la casa. Attendo i suoi comandi Padrone per eseguirli prontamente e rendere la sua vita piacevole e felice.\n"
        messaggio+="/now - mostra la temperatura\n"
        messaggio+="/ho_freddo - regola la temperatura\n"
        messaggio+="/ho_caldo - regola la temperatura\n"
        messaggio+="/casa - chi e' a casa?\n"
        messaggio+="/pulizie - attiva/disattiva modalita' pulizie\n"
        messaggio+="/turnon <ore> <temp> - attiva il riscaldamento per <ore> alla temperatura <temp>\n"
        messaggio+="/turnoff <ore> - disattiva il riscaldamento per <ore>\n"
        messaggio+="/annulla - disattiva il comando /turnon o /turnoff\n"
        messaggio+="/set [giorno sett] <ora> <temp>\n"
        messaggio+="/table\n"
        messaggio+="/all - mostra i dettagli dei sensori\n"
        messaggio+="Riscaldamento "
        if heating_status:
            messaggio+="attivato"
        else:
            messaggio+="disattivato"
        show_keyboard = {'hide_keyboard':False} #tastiera personalizzata
        result = bot.sendPhoto(CHAT_ID, open('MAGGIORDOMO.jpg', 'rb'), reply_markup=show_keyboard, disable_notification=debug_notify)
        bot.sendMessage(CHAT_ID, messaggio, reply_markup=show_keyboard, disable_notification=debug_notify)
    elif command == '/pulizie':
        if heating_overwrite:
            bot.sendMessage(CHAT_ID, "Modalita' overwrite attiva. fare /annulla prima di /pulizie",disable_notification=True)
        else:
            if not pulizie_status:
                # set 2 hours off for cleaning
                pulizie_status=True
                t=time.time()
                #lst=list(t)
                #if t + 2*60*60 <= t:
                #    lst[3]=23;
                #    lst[4]=59;
                #    pulizie_timer= time.mktime(tuple(lst))
                #else:
                pulizie_timer = t + 2*60*60 #2 hours
                if heating_status:
                    TurnOffHeating()
                    #GPIO.output(HEAT_PIN, HEAT_OFF) # sets port 0 to 0 (3.3V, off) per spengere i termosifoni
                bot.sendMessage(CHAT_ID, "Disattivo il riscaldamento Padrone cosi' puoi fare le pulizie", disable_notification=debug_notify)
            else:
                # set 2 hours off for cleaning
                pulizie_status=False
                if heating_status:
                    TurnOnHeating()
                    #GPIO.output(HEAT_PIN, HEAT_ON) # sets port 0 to 0 (3.3V, off) per spengere i termosifoni
                bot.sendMessage(CHAT_ID, "Modalita' pulizie disattivata")
    elif command == '/apri':
        bot.sendMessage(chat_id, "Confermi?", reply_markup= {'keyboard': [['SI'],['NO']], 'resize_keyboard':True})
        opengate_confirming=True
    elif opengate_confirming:
        if command == 'si':
            if GATE_ID == 0:
                GPIO.output(GATE_PIN, GATE_ON)
            else:
                setRadioGate(GATE_ID, GATE_ON)
            if str(chat_id) == str(CHAT_ID):
                bot.sendMessage(CHAT_ID, "Apro il cancello Padrone")
                bot.sendMessage(CHAT_ID, "Come ti posso aiutare?", reply_markup=main_show_keyboard, disable_notification=debug_notify)
            else:
                show_keyboard = {'keyboard': [['/apri']], 'resize_keyboard':True} #tastiera personalizzata
                bot.sendMessage(chat_id, "Apro il cancello, Visitatore della casa di "+nome_maggiordomo,disable_notification=True)
                bot.sendMessage(chat_id, "Premere /apri per aprire il cancello", reply_markup=show_keyboard,disable_notification=True)
                bot.sendMessage(CHAT_ID, msg_sender+" mi ha chiesto di aprire il cancello Padrone")
            time.sleep(2)
            if GATE_ID==0:
                GPIO.output(GATE_PIN, GATE_OFF)
            opengate_confirming=False
        else:
            opengate_confirming=False
            if str(chat_id) == str(CHAT_ID):
                bot.sendMessage(CHAT_ID, "Annullo come richiesto Padrone")
                bot.sendMessage(CHAT_ID, "Come ti posso aiutare?", reply_markup=main_show_keyboard)
            else:
                show_keyboard = {'keyboard': [['/apri']], 'resize_keyboard':True} #tastiera personalizzata
#            bot.sendMessage(chat_id, "Apro il cancello, Visitatore della casa Bellezza",disable_notification=True)
                bot.sendMessage(chat_id, "Premere /apri per aprire il cancello", reply_markup=show_keyboard,disable_notification=True)
    elif command == '/turnon':
        if pulizie_status:
            bot.sendMessage(CHAT_ID, "Modalita' pulizie attiva. Non puoi dare il comando /turnon",disable_notification=True)
        else:
            overwrite_duration = 1000 #default forever = 1000 ore
            overwrite_temp = 25     #default 25 gradi centigradi
            if num_args > 1:
                overwrite_duration = int(command_list[1])
                if num_args > 2:
                    overwrite_temp = int(command_list[2])
            overwrite_timer = time.time() + overwrite_duration*60*60 #2 hours
            if overwrite_duration == 1000:
                overwrite_message = "sempre"
            else:
                if overwrite_duration == 1:
                    overwrite_message = str(overwrite_duration)+" ora"
                else:
                    overwrite_message = str(overwrite_duration)+" ore"            
            heating_overwrite = True
            heating_status = True
            TurnOnHeating()
            bot.sendMessage(CHAT_ID, "Attivo overwrite per "+overwrite_message,disable_notification=True)
    elif command == '/turnoff':
        if pulizie_status:
            bot.sendMessage(CHAT_ID, "Modalita' pulizie attiva. Non puoi dare il comando /turnoff",disable_notification=True)
        else:
            overwrite_duration = 1000 #default forever = 1000 ore
            overwrite_temp = -5     #default 5 gradi centigradi (il segno meno e' per indicare turnOFF)
            if num_args > 1:
                overwrite_duration = int(command_list[1])
                if num_args > 2:
                    overwrite_temp = -int(command_list[2]) #il segno meno e' per indicare turnOFF
            overwrite_timer = time.time() + overwrite_duration*60*60 #2 hours
            if overwrite_duration == 1000:
                overwrite_message = "sempre"
            else:
                if overwrite_duration == 1:
                    overwrite_message = str(overwrite_duration)+" ora"
                else:
                    overwrite_message = str(overwrite_duration)+" ore"            
            heating_overwrite = True
            heating_status = False
            TurnOffHeating()
            bot.sendMessage(CHAT_ID, "Attivo overwrite per "+overwrite_message,disable_notification=True)
    elif command == '/restart':
        bot.sendMessage(CHAT_ID, "Riavvio "+nome_maggiordomo,disable_notification=True)
        result = subprocess.call(['sudo','supervisorctl','restart','MyS_Controller'])
        result = subprocess.call(['sudo','supervisorctl','restart','thermogram2'])
    elif command == '/reset':
        bot.sendMessage(CHAT_ID, "Resetto "+nome_maggiordomo,disable_notification=True)
        result = subprocess.call(['sudo','reboot','now'])
    elif command == '/cmd':
        if num_args > 1:
            cmd_str = ["" for x in range(num_args-1)]
            for i in range(1, num_args):
                cmd_str[i-1] = str(command_list[i])
#            cmd_str = cmd_str + "> \home\pi\git\\thermostat\\thermostat\\cmd_result.txt"
            bot.sendMessage(BOT_ASSISTANT_CHATID, "invio comando "+str(cmd_str),disable_notification=True)
#            bot.sendMessage(TOKEN, "invio comando "+str(cmd_str),disable_notification=True)
            result = subprocess.check_output(cmd_str)
            f = open(os.path.dirname(os.path.realpath(__file__)) + "/cmd_result.txt","w")  #apre il file dei dati in read mode
            f.write(result)  #legge la info del sensore sul file e divide per data, ora e valore
            f.close()  #chiude il file dei dati e lo salva
            trunk_result = result[:4000]
            bot.sendMessage(BOT_ASSISTANT_CHATID, "ho scritto il file di risultato: "+str(trunk_result),disable_notification=True)
#            bot.sendMessage(TOKEN, "ho scritto il file di risultato: "+str(trunk_result),disable_notification=True)
        else:
            bot.sendMessage(BOT_ASSISTANT_CHATID, "CMD senza parametri, padrone",disable_notification=True)
#            bot.sendMessage(TOKEN, "CMD senza parametri, padrone",disable_notification=True)
    elif command == '/noip':
        bot.sendMessage(CHAT_ID, "Avvio noip2",disable_notification=True)
        result = subprocess.call(['sudo','noip2'])
    elif command == '/cold_on':
        result = subprocess.call(['irsend','SEND_ONCE','BION','TURN_ON'])
        bot.sendMessage(CHAT_ID, "Accendo il condizionatore",disable_notification=True)
    elif command == '/cold_off':
        result = subprocess.call(['irsend','SEND_ONCE','BION','TURN_OFF'])
        bot.sendMessage(CHAT_ID, "Spengo il condizionatore",disable_notification=True)
    elif command == '/heat_on':
        heatpump_status = True
        TurnOnHeatpump()
        bot.sendMessage(CHAT_ID, "Accendo la pompa di calore",disable_notification=True)
    elif command == '/heat_off':
        heatpump_status = False
        TurnOffHeatpump()
        bot.sendMessage(CHAT_ID, "Spengo la pompa di calore",disable_notification=True)
    elif command == '/image':
        result = bot.sendPhoto(CHAT_ID, open('FER_IN.jpg', 'rb'))
    elif command == '/all':
        messaggio=""
        for i in range (NUM_SENSORI):
            messaggio+="("+sensori[i]+") T="+str("%0.1f" % float(sensor_value[i][1]))+" C, H="+str("%0.1f" % float(sensor_value[i][2]))+"%, Batt="+str("%0.1f" % float(sensor_value[i][3]))+"% t="+sensor_value[i][0]+"\n"
        bot.sendMessage(CHAT_ID, messaggio, disable_notification=debug_notify)
    else:
        bot.sendMessage(CHAT_ID, "'"+msg_username+" dice "+command+"'?? Puoi ripetere, Padrone? I miei circuiti sono un po' arrugginiti",disable_notification=True)
        bot.sendMessage(CHAT_ID, "Come ti posso aiutare?",disable_notification=True, reply_markup=main_show_keyboard)



############ legge da file il token del Telegram Bot e della chat id

tokenpath = os.path.dirname(os.path.realpath(__file__)) + "/token"
chatidpath = os.path.dirname(os.path.realpath(__file__)) + "/chatid"
chatidgatepath = os.path.dirname(os.path.realpath(__file__)) + "/chatid_cancello"
bot_assistant_chatidpath = os.path.dirname(os.path.realpath(__file__)) + "/BotAssistant.chatid"

try:
    tokenFile = open(tokenpath,'r')
    TOKEN = tokenFile.read().strip()
    tokenFile.close()
except IOError: 
    logging.error("Non ho trovato il file di token. E' necessario creare un file 'token' con la token telegram per il bot. In ogni caso questo file NON deve essere tracciato da git - viene ignorato perche' menzionato nel .gitignore.")
    exit()

logging.info("caricata token.")
print('Ho letto il token')
        
try:
    chatidFile = open(chatidpath,'r')
    CHAT_ID = chatidFile.read().strip()
    chatidFile.close()
except IOError:
    logging.error("Non ho trovato il file di chatId. E' necessario creare un file 'chatid' con la chatid telegram per il bot")
    # In ogni caso questo file NON deve essere tracciato da git - viene ignorato perche' menzionato nel .gitignore.")

logging.info("caricata chatId.")
print('Ho letto il chatId')

if GATE_PRESENT:
    try:
        chatidFile = open(chatidgatepath,'r')
        CHAT_ID_GATE = chatidFile.read().strip()
        chatidFile.close()
    except IOError:
        CHAT_ID_GATE = CHAT_ID #se non c'e' il cancello metto lo stesso chat_id principale
        logging.error("Non ho trovato il file di chatId_cancello. E' necessario creare un file 'chatid' con la chatid telegram per il bot")
        sys.exit(9)
        # In ogni caso questo file NON deve essere tracciato da git - viene ignorato perche' menzionato nel .gitignore.")

    logging.info("caricata chatIdGate.")
    print('Ho letto il chatIdGate')
    
    
#### legge il chatID del Maggiordomo Father

try:
    bot_assistant_chatidFile = open(bot_assistant_chatidpath,'r')
    BOT_ASSISTANT_CHATID = bot_assistant_chatidFile.read().strip()
    bot_assistant_chatidFile.close()
except IOError: 
    #logging.error("Non ho trovato il file di chatid. E' necessario creare un file 'BotAssistant.chatid' con la chatidi telegram per il bot. In ogni caso questo file NON deve essere tracciato da git - viene ignorato perche' menzionato nel .gitignore.")
    exit()
    
logging.info("caricata bot_assistant_chatId.")
print('Ho letto il bot_assistant_chatId')


# variables for periodic reporting
last_report = time.time()
report_interval = 300  # report every 300 seconds (5 min) as a default

# variable for heating status
heating_status = False
heating_standby = False
heating_overwrite = False

heatpump_status = False 

CurTempDHT = 0
CurHumidity = 0

# variables for cleaning period
pulizie_status=False
pulizie_timer=None


################# gestione della interfaccia di GPIO   
# wiringpi numbers  

import RPi.GPIO as GPIO

##import wiringpi2 as wiringpi
##wiringpi.wiringPiSetup()
##wiringpi.pinMode(0, 1) # sets WP pin 0 to output

GPIO.setmode(GPIO.BCM)
GPIO.setup(HEAT_PIN,GPIO.OUT)
GPIO.setup(HEAT2_PIN,GPIO.OUT)
GPIO.setup(GATE_PIN,GPIO.OUT)

#Find temperature from thermometer
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'
if DS_PRESENCE:
    device_folder = glob.glob(base_dir + '28*')[0]
    device_file = device_folder + '/w1_slave'
    
if DS1820_PRESENCE:
    device_folder = glob.glob(base_dir + '10*')[0]
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
    global DHT_TYPE
    
    if DHT_TYPE == 11:
        sensor = Adafruit_DHT.DHT11
    else:
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
        print (( 'Temp={0:0.1f}*C  Humidity={1:0.1f}%'.format(temperature, humidity)))
        return (temperature, humidity)
    else:
        print (('Failed to get reading. Try again!'))
        return (None, None)

########## fine gestione sensore DHT11 ############################

######### lettura sensori di temperatura #################

def read_sensors():
    global sensori, NUM_SENSORI, sensor_value, main_sensor
    for i in range (NUM_SENSORI):
        try:
            f = open("sensor"+str(i)+".log","r")  #apre il file dei dati in read mode
            value = f.read().split()  #legge la info del sensore sul file e divide per data, ora e valore
            f.close()  #chiude il file dei dati e lo salva
            sensor_value[i][0]= "%s" % str(value[0]) + " %s" % str(value[1])
            sensor_value[i][1]= "%.1f" % float(value[2])
            try:
                sensor_value[i][2]= "%.1f" % float(value[3])
            except:
                sensor_value[i][2]= 0.0
            try:
                sensor_value[i][3]= "%.1f" % float(value[4])
            except:
                sensor_value[i][3]= 0.0
        except IOError:
            sensor_value[i][1] = -99  #se il file non e' presente imposto il sensore a -99


######### FINE lettura sensori di temperatura ###########


##################### funzione per la gestione dei messaggi di presence

def set_presence(n, presence_msg):
    global persona_at_home, who_is_at_home, how_many_at_home, hide_notify
    global heating_status, heating_standby, heating_overwrite
    global CHAT_ID
    global debug_notify
    
    logging.debug('gestisco il messaggio di presence '+presence_msg)
    changed = False
    messaggio_IN_OUT = "null"
    
    if len(presence_msg) !=0:
        words = presence_msg.split(' ', 2)
        nome = words[0]
        status = words[1]
        try:
            IFTTTtime = words[2]
            print("IFTTTtime "+IFTTTtime)
            temp_str=IFTTTtime.rsplit(" ",1)
            if (temp_str[1].lower()=="casa") or (temp_str[1].lower()=="verrecchie"):
                print("sto gestendo la location")
                IFTTTtime=temp_str[0]
                location = temp_str[1].lower()
                print("IFTTTtime:"+IFTTTtime)
                print("location:"+location)
            else:
                print("orario letto da mail senza location:"+IFTTTtime)
            orario = time.strptime(IFTTTtime, "%B %d, %Y at %I:%M%p")
#            try:
#                orario = time.strptime(IFTTTtime, "%B %d, %Y at %I:%M%p")
#                print("orario letto da mail senza location:"+IFTTTtime)
#            except:
#                e = sys.exc_info()[0]
#                print( "<p>Error: %s</p>" % e )
#                print("sto gestendo la location")
#                temp_str=IFTTTtime.rsplit(" ", 1)
#                IFTTTtime = temp_str[0]
#                location = temp_str[1]
#                print("IFTTTtime:"+IFTTTtime)
#                print("location:"+location)
#                orario = time.strptime(IFTTTtime, "%B %d, %Y at %I:%M%p")
            print("orario letto da mail "+time.asctime(orario))
        except:
            e = sys.exc_info()[0]
            logging.error( "<p>Error: %s</p>" % e )
            orario = time.localtime(time.time())
        # scrive la info di presence su file

        localtime = time.asctime( orario )
        ora_minuti = time.strftime("%H:%M", orario)
        current_ora = int(time.strftime("%H", orario))
        
        filepresence = open("filepresence","a")  #apre il file dei dati in append mode, se il file non esiste lo crea
        filepresence.write(presence_msg+" "+localtime+"\n")  #scrive la info di presence ed il timestam sul file
        filepresence.close()  #chiude il file dei dati e lo salva
        
        changed = False
        
        if n == -1:
            try:
                n=persona.index(nome)
            except ValueError: #non ho riconosciuto la persona
                messaggio_IN_OUT = "Padrone verifica se ci sono sconosciuti in casa!"
                changed = True
                bot.sendMessage(CHAT_ID, "Padrone verifica se ci sono sconosciuti in casa!")
                return changed, messaggio_IN_OUT

        if status == 'IN':
            if persona_at_home[n] == False:
                persona_at_home[n] = True
                messaggio_IN_OUT="Benvenuto a casa "+nome+"\nSono le "+ora_minuti
                changed = True
                if NOTIFY_PRESENCE:
                    try:
                        res=bot.sendMessage(CHAT_ID, messaggio_IN_OUT ,disable_notification=hide_notify)
                        print(res)
                    except:
                        res=bot.sendMessage(CHAT_ID, '.'+messaggio_IN_OUT ,disable_notification=hide_notify)
                f = open(persona[n]+"_at_home","w")  #apre il file dei dati in write mode, se il file non esiste lo crea
                f.write("IN")  #scrive la info di presence sul file
                f.close()  #chiude il file dei dati e lo salva
                log_presence(localtime, persona[n], status)
        elif status == 'OUT':
            if persona_at_home[n]:
                persona_at_home[n] = False
                messaggio_IN_OUT="Arrivederci a presto "+nome+"\nSono le "+ora_minuti
                changed = True
                if NOTIFY_PRESENCE:
                    try:
                        res=bot.sendMessage(CHAT_ID, messaggio_IN_OUT ,disable_notification=hide_notify)
                        print(res)
                    except:
                        res=bot.sendMessage(CHAT_ID, '.'+messaggio_IN_OUT ,disable_notification=hide_notify)
                f = open(persona[n]+"_at_home","w")  #apre il file dei dati in write mode, se il file non esiste lo crea
                f.write("OUT")  #scrive la info di presence sul file
                f.close()  #chiude il file dei dati e lo salva
                log_presence(localtime, persona[n], status)

        # calcola chi e' a casa
        who_is_at_home=""
        how_many_at_home=0
        for n in range(persone_della_casa):
            if persona_at_home[n]:
                who_is_at_home=who_is_at_home+persona[n]+" "
                how_many_at_home=how_many_at_home+1
    
        print ((str(how_many_at_home)+"  "+who_is_at_home))
	
        # scrive su file quante persone sono a casa per MySController
        f = open("how_many_at_home","w")
        f.write(str(how_many_at_home))
        f.close()  #chiude il file dei dati e lo salva
    
        if how_many_at_home == 0: #nessuno in casa
            if heating_standby == False:  #standby termosifoni non attivo
                heating_standby = True
                f = open("heating_standby","w")
                f.write('ON')
                f.close()  #chiude il file dei dati e lo salva
                if not heating_overwrite and heating_status: #se termosifoni attivi
                    if FORCE_HOUR[current_ora] == 0:
                        TurnOffHeating()
                        #GPIO.output(HEAT_PIN, HEAT_OFF) # spenge i termosifoni
                        try:
                            bot.sendMessage(CHAT_ID, "Ho messo in stand by il riscaldamento in attesa che rientri qualcuno a casa",disable_notification=True)
                        except:
                            bot.sendMessage(CHAT_ID, ".Ho messo in stand by il riscaldamento in attesa che rientri qualcuno a casa",disable_notification=True)
        else: #almeno una persona in casa
            if heating_standby: #se standby attivo
                heating_standby = False
                f = open("heating_standby","w")
                f.write('OFF')
                f.close()  #chiude il file dei dati e lo salva
                if not heating_overwrite and heating_status: #se termosifoni attivi prima dello standby
                    TurnOnHeating()
                    #GPIO.output(HEAT_PIN, HEAT_ON) # riaccende i termosifoni
                    try:
                        bot.sendMessage(CHAT_ID, "Ho riavviato il riscaldamento per il tuo confort, Padrone",disable_notification=True)
                    except:
                        bot.sendMessage(CHAT_ID, ".Ho riavviato il riscaldamento per il tuo confort, Padrone",disable_notification=True)
        # inserito retur per debug
    return changed, messaggio_IN_OUT
    #return set_presence            


######################## check presence con ping IP su wifi


def check_presence_IP():
    global persona_IP, persona_at_home, persone_della_casa, persona_ARP
    global CHAT_ID
    for n in range(persone_della_casa):
#        result = os.system("ping -c 2 " + persona_IP[n])
        if persona_ARP[n] == "1":
            result = subprocess.call(['ping','-c','1',persona_IP[n]])
            if (result == 0):
                if not persona_at_home[n]:
                    changed, messaggio_IN_OUT= set_presence(n, persona[n]+' IN') #richiama la funzione per la gestisce della presence
#                   if changed:
#                       bot.sendMessage(CHAT_ID, messaggio_IN_OUT)
            else:
                if persona_at_home[n]:
                    changed, messaggio_IN_OUT= set_presence(n, persona[n]+' OUT') #richiama la funzione per la gestisce della presence
#                    if changed:
#                        bot.sendMessage(CHAT_ID, messaggio_IN_OUT)

####################################################

############# controlla la presence con ping BT #################        
def check_presence_BT():
    global persona_BT, persona_at_home, persone_della_casa, persona_ARP
    global CHAT_ID
    for n in range (persone_della_casa):
        if persona_ARP[n]=="1":
            result = bluetooth.lookup_name(persona_BT[n], timeout=5)
            if (result != None):
                if not persona_at_home[n]:
                    changed, messaggio_IN_OUT= set_presence(n, persona[n]+' IN') #richiama la funzione per la gestisce della presence
#                   if changed:
#                       bot.sendMessage(CHAT_ID, messaggio_IN_OUT)

            else:
                if persona_at_home[n]:
                    changed, messaggio_IN_OUT= set_presence(n, persona[n]+' OUT') #richiama la funzione per la gestisce della presence
#                   if changed:
#                       bot.sendMessage(CHAT_ID, messaggio_IN_OUT)

###################################################

import binascii

######################## check presence con ping arp su wifi
def check_presence_arp():
    global persona_IP, persona_at_home, persone_della_casa, persona_retry, persona_ARP, persona_WIFI, presence_MAC
    global CHAT_ID

    arp_result = str(subprocess.check_output(['sudo','/usr/bin/arp-scan','-l','-r','11']))
#    arp_result = art_result_b.decode('ascii')
    print (arp_result)
    
    for n in range(persone_della_casa):
        if persona_ARP[n]=="1":
#            result = os.system("ping -c 2 " + persona_IP[n])
###            tmp_ip_address = persona_IP[n]+'/32'
#iphone=$(/usr/bin/arp-scan --interface=eth0 -r 10 -q $ip_iphone/32|grep $ip_iphone|uniq|grep -c $ip_iphone)
###            arp_result = str(subprocess.check_output(['/usr/bin/arp-scan','--interface=wlan0','-r','10','-q',tmp_ip_address]))
#           print(arp_result)
            if PRESENCE_MAC:
                print(persona_WIFI[n])
                result = arp_result.find(persona_WIFI[n])
            else:   
                print(persona_IP[n])
                result = arp_result.find(persona_IP[n])
#        print(tmp_ip_address)
#        print (result)
            print('result['+str(n)+']='+str(result))
            
            if result > 0:  #persona at home
                persona_retry[n]=0
                if not persona_at_home[n]:
                    changed, messaggio_IN_OUT= set_presence(n, persona[n]+' IN') #richiama la funzione per la gestisce della presence
#                    if changed:
#                        bot.sendMessage(CHAT_ID, messaggio_IN_OUT)
            else:
                if persona_at_home[n]:
                    persona_retry[n]+=1
                    if persona_retry[n]>=PRESENCE_RETRY:
                        changed, messaggio_IN_OUT= set_presence(n, persona[n]+' OUT') #richiama la funzione per la gestisce della presence
                        persona_retry[n]=0
#                    if changed:
#                        bot.sendMessage(CHAT_ID, messaggio_IN_OUT)

####################################################


##### connette o riconnette alla mail ###########
def connect(retries=5, delay=3):
    global EMAIL_ID, EMAIL_PASSWD
    while True:
        try:
            mail = imaplib.IMAP4_SSL(imap_host)
            mail.login(EMAIL_ID,EMAIL_PASSWD)
            print ("ho connesso la mail")
            return mail
        except imaplib.IMAP4_SSL.abort:
            if retries > 0:
                retries -= 1
                time.sleep(delay)
            else:
                raise
#################################################

############## gestione del riscaldamento ##################
def setRadioHeat(xID, heat_toggle):
    if xID == 0:
        GPIO.output(HEAT_PIN, HEAT_OFF) # spengo la caldaia primaria
        GPIO.output(HEAT2_PIN, HEAT_OFF) # spengo la stufa secondaria
    else:
        f = open("heat_toggle","w")
        f.write(heat_toggle)
        f.close()  #chiude il file dei dati e lo salva
    return()

def TurnOnHeating():
    global heating_status, heating_standby, heating_overwrite, FILEHEATING, CHAT_ID
    global HEAT_PIN, HEAT2_PIN, HEAT_ON, HEAT_OFF, SECONDARY_HEAT, MAIN_HEAT, FORCE_HOUR

    orario = time.localtime(time.time())
    ora_attuale = int(time.strftime("%H", orario))
    giorno_attuale = int(time.strftime("%w", orario))

    heating_status = True #print "HEATING ON "+localtime+"\n"
    f = open("heating_status","w")
    f.write('ON')
    f.close()  #chiude il file dei dati e lo salva
    
    if not heating_overwrite and heating_standby and FORCE_HOUR[ora_attuale] == 0:
        try:
            bot.sendMessage(CHAT_ID, "Fa un po' freddo, Padrone, ma sono solo a casa e faccio un po' di economia")
        except:
            bot.sendMessage(CHAT_ID, ".Fa un po' freddo, Padrone, ma sono solo a casa e faccio un po' di economia")
        if HEAT_ID == 0:
            GPIO.output(HEAT_PIN, HEAT_OFF) # spengo la caldaia primaria
            GPIO.output(HEAT2_PIN, HEAT_OFF) # spengo la stufa secondaria
        else:
            setRadioHeat(HEAT_ID,"OFF")
    else:
        if SECONDARY_HEAT:
            if MAIN_HEAT[ora_attuale] == 1: # devo utilizzare la caldaia principale
                GPIO.output(HEAT2_PIN, HEAT_OFF) # spengo la stufa secondaria
                print('spengo la stufa secondaria')
                GPIO.output(HEAT_PIN, HEAT_ON) # accendo la caldaia primaria
                print('accendo la caldaia primaria')
            else: # devo utilizzare la caldaia secondaria
                GPIO.output(HEAT_PIN, HEAT_OFF) # spengo la caldaia primaria
                print('spengo la caldaia primaria')
                GPIO.output(HEAT2_PIN, HEAT_ON) # accendo la stufa secondaria
                print('accendo la stufa secondaria')
        else: # c'e' solo la caldaia primaria e l'accendo
            if HEAT_ID == 0:
                GPIO.output(HEAT_PIN, HEAT_ON) # sets port 0 to 1 (3.3V, on) per accendere i termosifoni
            else:
                setRadioHeat(HEAT_ID,"ON")
            print('accendo la caldaia unica')
        try:
            bot.sendMessage(CHAT_ID, "Accendo il riscaldamento, Padrone")
        except:
            bot.sendMessage(CHAT_ID, ".Accendo il riscaldamento, Padrone")
        orario = time.localtime(time.time())
        localtime = time.asctime( orario )
        ora_minuti = time.strftime("%H:%M", orario)
        fileheating = open(FILEHEATING,"a")  #apre il file dei dati in append mode, se il file non esiste lo crea
        fileheating.write("ON,"+localtime+"\n")  #scrive la info di accensione del riscaldamento il timestamp su file
        fileheating.close()  #chiude il file dei dati e lo salva

    
    
def TurnOffHeating():
    global heating_status, heating_standby, heating_overwrite, FILEHEATING, CHAT_ID
    global HEAT_PIN, HEAT2_PIN, HEAT_ON, HEAT_OFF, SECONDARY_HEAT, MAIN_HEAT

    heating_status = False
    f = open("heating_status","w")
    f.write('OFF')
    f.close()  #chiude il file dei dati e lo salva
    
    if HEAT_ID == 0:
        GPIO.output(HEAT_PIN, HEAT_OFF) # spengo la caldaia primaria
    else:
        setRadioHeat(HEAT_ID,"OFF")
    print('spengo la caldaia primaria o unica')
    if SECONDARY_HEAT: # se c'e' la stufa secondaria, la spengo
        GPIO.output(HEAT2_PIN, HEAT_OFF) # spengo la stufa secondaria
        print('spengo la stufa secondaria')
    
    try:
        bot.sendMessage(CHAT_ID, "Spengo il riscaldamento, Padrone")
    except:
        bot.sendMessage(CHAT_ID, ".Spengo il riscaldamento, Padrone")
    orario = time.localtime(time.time())
    localtime = time.asctime( orario )
    ora_minuti = time.strftime("%H:%M", orario)
    fileheating = open(FILEHEATING,"a")  #apre il file dei dati in append mode, se il file non esiste lo crea
    fileheating.write("OFF,"+localtime+"\n")  #scrive la info di accensione del riscaldamento il timestamp su file
    fileheating.close()  #chiude il file dei dati e lo salva

############## gestione della pompa di calore ##################
def setRadioHeatpump(xID, heatpump_toggle):
    f = open("heatpump_toggle","w")
    f.write(heatpump_toggle)
    f.close()  #chiude il file dei dati e lo salva
    return()

def TurnOnHeatpump():
    global heatpump_status, FILEHEATPUMP, CHAT_ID, HEATPUMP_ID

    orario = time.localtime(time.time())
    ora_attuale = int(time.strftime("%H", orario))
    giorno_attuale = int(time.strftime("%w", orario))

    heatpump_status = True #print "HEATPUMP ON "+localtime+"\n"
    f = open("heatpump_status","w")
    f.write('ON')
    f.close()  #chiude il file dei dati e lo salva
    
    setRadioHeatpump(HEATPUMP_ID,"ON")
    print('accendo la pompa di calore')
    try:
        bot.sendMessage(CHAT_ID, "Accendo la pompa di calore, Padrone")
    except:
        bot.sendMessage(CHAT_ID, ".Accendo la pompa di calore, Padrone")
    orario = time.localtime(time.time())
    localtime = time.asctime( orario )
    ora_minuti = time.strftime("%H:%M", orario)
    fileheatpump = open(FILEHEATPUMP,"a")  #apre il file dei dati in append mode, se il file non esiste lo crea
    fileheatpump.write("ON,"+localtime+"\n")  #scrive la info di accensione del riscaldamento il timestamp su file
    fileheatpump.close()  #chiude il file dei dati e lo salva

    
    
def TurnOffHeatpump():
    global heatpump_status, FILEHEATPUMP, CHAT_ID, HEATPUMP_ID

    heatpump_status = False
    f = open("heatpump_status","w")
    f.write('OFF')
    f.close()  #chiude il file dei dati e lo salva
    
    setRadioHeatpump(HEATPUMP_ID,"OFF")
    print('spengo la pompa di calore')
    try:
        bot.sendMessage(CHAT_ID, "Spengo la pompa di calore, Padrone")
    except:
        bot.sendMessage(CHAT_ID, ".Spengo la pompa di calore, Padrone")
    orario = time.localtime(time.time())
    localtime = time.asctime( orario )
    ora_minuti = time.strftime("%H:%M", orario)
    fileheating = open(FILEHEATPUMP,"a")  #apre il file dei dati in append mode, se il file non esiste lo crea
    fileheating.write("OFF,"+localtime+"\n")  #scrive la info di accensione del riscaldamento il timestamp su file
    fileheating.close()  #chiude il file dei dati e lo salva

##################### inizio gestione presence via email ################
#connect to gmail
def read_gmail():
    global mail
    global CHAT_ID
    print('leggo mail')
    
    try:
        mail.select('inbox')
#        print('mail.select')
        mail.list()
#        print('mail.list')
    # Any Emails? 
        n=0
        (retcode, messages) = mail.search(None, '(UNSEEN)')
#        print('mail.search')
        if retcode == 'OK':
            for num in messages[0].split() :
#                print('Processing new emails...')
                n=n+1
                typ, data = mail.fetch(num,'(RFC822)')
#                print('mail.fetch')
                for response_part in data:
                    if isinstance(response_part, tuple):
#                        print('isistance')
#                        print('response_part')
#                        print(response_part)
#                        print('------------- [1]')
#                        print(response_part[1])
                        try:
                            original = email.message_from_bytes(response_part[1])
                        except:
                            original = email.message_from_string(response_part[1])
#                        print('original')
#                        print(original)
                        subject_text=str(original['Subject'])
#                        print("subject_text:"+subject_text)
                        changed, messaggio_IN_OUT= set_presence(-1, subject_text) #richiama la funzione per la gestisce della presence
#                       if changed:
#                           bot.sendMessage(CHAT_ID, messaggio_IN_OUT)
#                        print('set_presence')
                        typ, data = mail.store(num,'+FLAGS','\\Seen') #segna la mail come letta
#                        print('mail.store')
                print(("Ho gestito "+str(n)+" messaggi di presence"))
    except:
        print('Errore nella lettura della mail')
        mail = connect()

############################### fine gestione presence via email #######################

############################ TEST Internet connection #############
import socket
REMOTE_SERVER = "www.google.com"
def is_connected():
    global REMOTE_SERVER
    now = time.time()
    localtime = time.asctime( time.localtime(now) )
    try:
        # see if we can resolve the host name -- tells us if there is
        # a DNS listening
        host = socket.gethostbyname(REMOTE_SERVER)
        # connect to the host -- tells us if the host is actually
        # reachable
        s = socket.create_connection((host, 80), 2)
        return True
    except Exception as e:
        logging.exception("www.google.com not reachable at "+str(localtime))
        pass
    return False
######### fine test internet connection

# -------------------- inizio programma

print('INIZIO IL PROGRAMMA THERMOGRAM')

######## Inizializza le temperature
if DS_PRESENCE or DS1820_PRESENCE:
    CurTemp = read_temp()
else:
    CurTemp = 99
    
if DHT_PRESENCE:
    CurTempDHT, CurHumidity = read_TandH()
else:
    CurTempDHT = 99
    CurHumidity = 0

############ legge da file lo stato delle persone della casa ###############
for n in range(persone_della_casa):
    persona_retry[n]=0
    try:
        f = open(persona[n]+"_at_home","r")  #apre il file dei dati in read mode
        pres=f.read().strip()   #legge la info di presence sul file
        f.close()  #chiude il file dei dati e lo salva
        if pres == "IN":
            persona_at_home[n] = True
        else:
            persona_at_home[n] = False
    except IOError:
        persona_at_home[n] = False  #se il file non e' presente imposto la presence a False

# calcola chi e' a casa
how_many_at_home=0
for n in range(persone_della_casa):
    if persona_at_home[n]:
         how_many_at_home=how_many_at_home+1
    
# scrive su file quante persone sono a casa per MySController
f = open("how_many_at_home","w")
f.write(str(how_many_at_home))
f.close()  #chiude il file dei dati e lo salva

######## legge da file lo stato del riscaldamento e dello standby ###########
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

heating_overwrite = False

######## legge da file lo programmazione del cronotermostato ###########
#### old initialize_schedule()
get_tempschedule()

######## inizializza il bot Telegram ###########
print('token: '+str(TOKEN))

bot = telepot.Bot(TOKEN)
print('avviato il bot')


#clear queue
updates = bot.getUpdates()
if updates:
    last_update_id = updates[-1]['update_id']
    bot.getUpdates(offset=last_update_id+1)

bot.message_loop(handle)
logging.info("Listening ...")

help_or_gate = '/help'
if GATE_PRESENT:
    help_or_gate = '/apri'

main_show_keyboard = {'keyboard': [['/now','/casa'], ['/ho_caldo','/ho_freddo'],['/turnon 1','/annulla'],['/pulizie',help_or_gate]]} #tastiera personalizzata
if male_maggiordomo:
    sex_indicator="o"
else:
    sex_indicator="a"
welcome_message = nome_maggiordomo+" si e' appena svegliat"+sex_indicator+", Padrone"
try:
    bot.sendMessage(CHAT_ID, welcome_message, disable_notification=debug_notify)
except:
    bot.sendMessage(CHAT_ID, "."+welcome_message, disable_notification=debug_notify)

if heating_status and not heating_standby:
    TurnOnHeating()
    bot.sendMessage(CHAT_ID, "Rispristino il riscaldamento, Padrone", disable_notification=debug_notify)
else:
    TurnOffHeating()

GPIO.output(GATE_PIN, GATE_OFF) #pulisce il circuito di apertura cancello

bot.sendMessage(CHAT_ID, 'Come ti posso aiutare?', reply_markup=main_show_keyboard, disable_notification=debug_notify)

#predispone la tastiera per i visitatori della casa
if GATE_PRESENT:
    show_keyboard = {'keyboard': [['/apri']], 'resize_keyboard':True} #tastiera personalizzata
    try:
        bot.sendMessage(CHAT_ID_GATE, "Premere /apri per aprire il cancello", reply_markup=show_keyboard, disable_notification=debug_notify)
    except:
        bot.sendMessage(CHAT_ID_GATE, ".Premere /apri per aprire il cancello", reply_markup=show_keyboard, disable_notification=debug_notify)

mail = connect() #apre la casella di posta

now = time.time()
orario = time.localtime(now)
curr_hour=int(time.strftime("%H",orario))
previous_heat = MAIN_HEAT[curr_hour] #previous_heat e' la caldaia dell'ora precedente
overwrite_timer = now #inizializza overwrite_timer
pulizie_status = False #inizializza pulizie status
pulizie_timer = now #inizializza pulizie_timer

while True:
    now = time.time()
    localtime = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    orario = time.localtime(now)
    curr_hour=int(time.strftime("%H",orario))
    
    CurTargetTemp=current_target_temp()
    if DS_PRESENCE or DS1820_PRESENCE:
        CurTemp = read_temp()
    if DHT_PRESENCE:
        CurTempDHT, CurHumidity = read_TandH()
        if (DS_PRESENCE and DS1820_PRESENCE) == False:
            CurTemp = CurTempDHT
    if CurHumidity == None:
        CurHumidity = 0

    ######## scrive il file del sensore 0 ---- da spostare nella routine che gestisce la lettura delle temperature        
    f = open("sensor0.log","w")  #apre il file dei dati in read mode
    f.write(localtime+" "+str(CurTemp)+" "+str(CurHumidity))  #legge la info del sensore sul file e divide per data, ora e valore
    f.close()  #chiude il file dei dati e lo salva
            
    read_sensors()
    
    CurTemp = float(sensor_value[main_sensor][1])
    ExtTemp = 0
    if ExtTempID != -99:
        ExtTemp = float(sensor_value[ExtTempID][1])
    
    current_heat = MAIN_HEAT[curr_hour] #current_heat e' la caldaia dell'ora attuale
    change_heat = (current_heat != previous_heat)
    if change_heat:
        previous_heat = current_heat
        
#    if heating_overwrite and heating_status and change_heat:
    if heating_status and change_heat:
        TurnOnHeating()
    if heating_overwrite:
        if now >= overwrite_timer:
            heating_overwrite = False
            try:
                bot.sendMessage(CHAT_ID, "E'terminato il periodo di overwrite",disable_notification=True)
            except:
                bot.sendMessage(CHAT_ID, ".E'terminato il periodo di overwrite",disable_notification=True)
        else: #ancora non e' terminato il periodo di overwrite
            if overwrite_temp > 0:  #overwrite settato a turnON
                if not heating_status:
                    if CurTemp < (overwrite_temp - 0.2):
                        TurnOnHeating()
                else:
                    if CurTemp > (overwrite_temp + 0.2):
                        TurnOffHeating()
            else: #overwrite settato a turnOFF
                if not heating_status:
                    if CurTemp < (-overwrite_temp - 0.2):
                        TurnOnHeating()
                else:
                    if CurTemp > (-overwrite_temp + 0.2):
                        TurnOffHeating()
    else:  #not heating_overwrite
        if pulizie_status:
            if now >= pulizie_timer:
                pulizie_status=False
                try:
                    bot.sendMessage(CHAT_ID, "E' terminato il periodo per le pulizie, Padrone", disable_notification=debug_notify)
                except:
                    bot.sendMessage(CHAT_ID, ".E' terminato il periodo per le pulizie, Padrone", disable_notification=debug_notify)
        else:
            if not heating_status:
                if CurTemp < (CurTargetTemp - 0.2):
                    TurnOnHeating()
            else:
                if CurTemp > (CurTargetTemp + 0.2):
                    TurnOffHeating()
    if report_interval is not None and last_report is not None and now - last_report >= report_interval:
        if DHT_PRESENCE:
            CurTempDHT, CurHumidity = read_TandH()
        else:
            CurTempDHT = 99
            CurHumidity = 0
        #apre il file dei dati in append mode, se il file non esiste lo crea
        filedati = open("filedati","a")
        #scrive la temperatura corrente ed il timestam sul file
        filedati.write("T="+str(CurTemp)+",HR="+str(CurHumidity)+"@"+localtime+"\n")
        #chiude il file dei dati e lo salva
        filedati.close()
        log_temperature(localtime,CurTemp,CurTempDHT,CurHumidity, ExtTemp, (heating_status and not heating_standby), CurTargetTemp)
        last_report = now
    # verifica se ci sono nuovi aggiornamenti sulla presence (via email)
    if is_connected():
        read_gmail()
            
    #check_presence_BT()
    if IP_PRESENCE:
        check_presence_IP() # controlla la presente con ping IP
    if BT_PRESENCE:
        check_presence_BT()
    if ARP_PRESENCE:
        check_presence_arp()
        
    time.sleep(60)

