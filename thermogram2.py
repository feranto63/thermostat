#!/usr/bin/python
# DEFINIZIONE VARIABILI DI PERSONALIZZAZIONE
import sys

PROPRIETARIO = sys.argv[1]  # get user from command-line
owner_found = False

if PROPRIETARIO == 'Ferruccio':
    persone_della_casa = 4
    persona=['Ferruccio','Claudia','Riccardo','Lorenzo']
    persona_at_home=[True, True, True, True]
    imap_host = 'imap.gmail.com'
    EMAIL_ID='MaggiordomoBot@gmail.com'
    EMAIL_PASSWD='cldbzz00'
    Ferruccio_BT = 'F0:5B:7B:43:42:68'       #Galaxy S6 edge+
    #80:19:34:A3:7A:A9       NBW72009135393 (PC portatile ASUS)
    Claudia_BT = '50:FC:9F:85:BE:F2'         #Claudia Note 3
    #8C:C8:CD:31:D1:B1       DTVBluetooth TV Sony
    Citroen_C3_BT = '00:26:7E:C7:0B:07'      #Parrot MINIKIT+ v1.22
    Lorenzo_BT = 'B4:3A:28:CC:C6:07'         #Lorenzo S5
    persona_IP=['192.168.1.38','192.168.1.5','192.168.1.2','192.168.1.37'] #IP address of smartphone; fixed assignment by router
    persona_BT=['F0:5B:7B:43:42:68','50:FC:9F:85:BE:F2','00:00:00:00:00:00','B4:3A:28:CC:C6:07'] #BT mac address of smartphone
    GATE_PRESENT = False
    IP_PRESENCE = True
    BT_PRESENCE = False
    owner_found=True

if PROPRIETARIO == 'Piero':
    persone_della_casa = 2
    persona=['Piero','Annamaria']
    persona_at_home=[True, True]
    imap_host = 'imap.gmail.com'
    EMAIL_ID='BattistaMaggiordomoBot@gmail.com'
    EMAIL_PASSWD='peterbel'
    persona_IP=['192.168.0.0','192.168.0.0','192.168.0.0','192.168.0.0'] #IP address of smartphone; fixed assignment by router
    persona_BT=['00:00:00:00:00:00','00:00:00:00:00:00','00:00:00:00:00:00','00:00:00:00:00:00'] #BT mac address of smartphone
    GATE_PRESENT = True
    IP_PRESENCE = False
    BT_PRESENCE = False
    owner_found=True

if not owner_found:
    sys.exit("owner not found")


FILESCHEDULE="fileschedule"
FILEHEATING="fileheating"
HEAT_ON  = 0
HEAT_OFF = 1
HEAT_PIN = 17
GATE_PIN = 22
GATE_ON = 0
GATE_OFF = 1
DHT_PIN = 4

lucchetto_chiuso = u'\U0001f512' # '\xF0\x9F\x94\x92'  #	lock U+1F512
lucchetto_aperto = u'\U0001f513' # '\xF0\x9F\x94\x93'  #    open lock U+1F513	


#imports for thermometer reading
import os
import glob
import time
#imports for gmail reading
import imaplib
import email
#import for Telegram API
import pprint
import telepot

import requests

import bluetooth

#import library for logging
import logging
logging.basicConfig(filename='termostato.log', level=logging.WARNING)

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
   
    curr_year=int(time.strftime("%Y",orario))
    curr_month=int(time.strftime("%m",orario)) 
    curr_day=int(time.strftime("%e",orario))
    curr_hour=int(time.strftime("%H",orario))

    localtime = time.asctime( orario )
    day_of_week= calendar.weekday(curr_year,curr_month,curr_day)

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

################### fine gestione cronotermostato ######################

###################### gestisce i comandi inviati al Telegram Bot
def handle(msg):
    global persona_at_home
    global last_report, report_interval     #parametri per il monitoraggio su file delle temperature
    global heating_status, heating_standby, heating_overwrite  #stato di accensione dei termosifoni
    global who_is_at_home, how_many_at_home
    global mySchedule, CurTargetTemp
    global CHAT_ID, GATE_PRESENT
    global pulizie_status, pulizie_timer
    
    logging.debug('inizio la gestione di handle')
    msg_type, chat_type, chat_id = telepot.glance(msg)
    msg_sender = msg['from']['first_name']
    
    # ignore non-text message
    if msg_type != 'text':
        return

    command = msg['text'].strip().lower()
    CurTemp = read_temp()
    CurTargetTemp=current_target_temp()
    
    orario = time.localtime(time.time())
    localtime = time.asctime( orario )
    giorno_ora_minuti = time.strftime("%a %H:%M", orario)
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
        messaggio="La temperatura misurata e' di "+str("%0.1f" % CurTemp)+" C, Padrone\n"
        messaggio+="La temperatura di confort e' di "+str(CurTargetTemp)+" C\n"
        messaggio+="Il riscaldamento e' "
        if pulizie_status:
            messaggio+="disattivato per pulizie"
        else:
            messaggio+=heatstat
        bot.sendMessage(CHAT_ID, messaggio)
    elif command == '/annulla':
        heating_overwrite = False
        bot.sendMessage(CHAT_ID, "Annullo overwrite")
    elif command == '/ho_freddo':
        bot.sendMessage(CHAT_ID, "Ho capito che hai freddo")
        f = open("heating_update","a")
        f.write("F,"+heatstat+","+giorno_ora_minuti+","+str("%0.1f" % CurTemp)+","+str(CurTargetTemp)+"\n")
        f.close()  #chiude il file dei dati e lo salva
    elif command == '/ho_caldo':
        bot.sendMessage(CHAT_ID, "Funzionalita' in sviluppo")
        bot.sendMessage(CHAT_ID, "Ho capito che hai caldo")
        f = open("heating_update","a")
        f.write("C,"+heatstat+","+giorno_ora_minuti+","+str("%0.1f" % CurTemp)+","+str(CurTargetTemp)+"\n")
        f.close()  #chiude il file dei dati e lo salva
    elif command == '/casa':
        who_is_at_home=""
        how_many_at_home=0
        for who_at_home in range(persone_della_casa):
            if persona_at_home[who_at_home]:
                who_is_at_home+=persona[who_at_home]+" "
                how_many_at_home+=1
        if how_many_at_home != 0:
            if how_many_at_home == 1:
                bot.sendMessage(CHAT_ID, who_is_at_home+"e' a casa")
            else:
                bot.sendMessage(CHAT_ID, who_is_at_home+"sono a casa")
        else:
            bot.sendMessage(CHAT_ID, "Sono solo a casa, Padrone")
    elif command == '/help':
        # send message for help
        messaggio="Sono il Maggiordomo e custodisco la casa. Attendo i suoi comandi Padrone per eseguirli prontamente e rendere la sua vita piacevole e felice.\n"
        messaggio+="/now - mostra la temperatura\n"
        messaggio+="/ho_freddo - accende il riscaldamento\n"
        messaggio+="/ho_caldo - spegne il riscaldamento\n"
        messaggio+="/casa - chi e' a casa?\n"
        messaggio+="Riscaldamento "
        if heating_status:
            messaggio+="attivato"
        else:
            messaggio+="disattivato"
        bot.sendMessage(CHAT_ID, messaggio)
    elif command == '/pulizie':
        if not pulizie_status:
            # set 2 hours off for cleaning
            pulizie_status=True
            pulizie_timer = time.time() + 2*60*60 #2 hours
            if heating_status:
                TurnOffHeating()
                #GPIO.output(HEAT_PIN, HEAT_OFF) # sets port 0 to 0 (3.3V, off) per spengere i termosifoni
            bot.sendMessage(CHAT_ID, "Disattivo il riscaldamento Padrone cosi' puoi fare le pulizie")
        else:
            # set 2 hours off for cleaning
            pulizie_status=False
            if heating_status:
                TurnOnHeating()
                #GPIO.output(HEAT_PIN, HEAT_ON) # sets port 0 to 0 (3.3V, off) per spengere i termosifoni
            bot.sendMessage(CHAT_ID, "Modalita' pulizie disattivata")
    elif command == '/apri':
        GPIO.output(GATE_PIN, GATE_ON)
        if str(chat_id) == str(CHAT_ID):
            bot.sendMessage(CHAT_ID, "Apro il cancello Padrone")
        else:
            show_keyboard = {'keyboard': [['/apri']], 'resize_keyboard':True} #tastiera personalizzata
            bot.sendMessage(chat_id, "Apro il cancello, Visitatore della casa Bellezza")
            bot.sendMessage(chat_id, "Premere /apri per aprire il cancello", reply_markup=show_keyboard)
            bot.sendMessage(CHAT_ID, msg_sender+" mi ha chiesto di aprire il cancello Padrone")
        time.sleep(2)
        GPIO.output(GATE_PIN, GATE_OFF)
    elif command == '/turnon':
        heating_overwrite = True
        TurnOnHeating()
        bot.sendMessage(CHAT_ID, "Attivo overwrite")
    elif command == '/turnoff':
        heating_overwrite = True
        TurnOffHeating()
        bot.sendMessage(CHAT_ID, "Attivo overwrite")
    else:
        bot.sendMessage(CHAT_ID, "Puoi ripetere, Padrone? I miei circuiti sono un po' arrugginiti")



############ legge da file il token del Telegram Bot e della chat id

tokenpath = os.path.dirname(os.path.realpath(__file__)) + "/token"
chatidpath = os.path.dirname(os.path.realpath(__file__)) + "/chatid"
chatidgatepath = os.path.dirname(os.path.realpath(__file__)) + "/chatid_cancello"


try:
    tokenFile = open(tokenpath,'r')
    TOKEN = tokenFile.read().strip()
    tokenFile.close()
except IOError: 
    logging.error("Non ho trovato il file di token. E' necessario creare un file 'token' con la token telegram per il bot. In ogni caso questo file NON deve essere tracciato da git - viene ignorato perche' menzionato nel .gitignore.")
    exit()

logging.info("caricata token.")
        
try:
    chatidFile = open(chatidpath,'r')
    CHAT_ID = chatidFile.read().strip()
    chatidFile.close()
except IOError:
    logging.error("Non ho trovato il file di chatId. E' necessario creare un file 'chatid' con la chatid telegram per il bot")
    # In ogni caso questo file NON deve essere tracciato da git - viene ignorato perche' menzionato nel .gitignore.")

logging.info("caricata chatId.")

try:
    chatidFile = open(chatidgatepath,'r')
    CHAT_ID_GATE = chatidFile.read().strip()
    chatidFile.close()
except IOError:
    CHAT_ID_GATE = CHAT_ID #se non c'e' il cancello metto lo stesso chat_id principale
    logging.error("Non ho trovato il file di chatId_cancello. E' necessario creare un file 'chatid' con la chatid telegram per il bot")
    # In ogni caso questo file NON deve essere tracciato da git - viene ignorato perche' menzionato nel .gitignore.")

logging.info("caricata chatIdGate.")


# variables for periodic reporting
last_report = time.time()
report_interval = 300  # report every 300 seconds (5 min) as a default

# variable for heating status
heating_status = False
heating_standby = False
heating_overwrite = False

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
GPIO.setup(GATE_PIN,GPIO.OUT)

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
    sensor = Adafruit_DHT.DHT11
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


##################### funzione per la gestione dei messaggi di presence
def set_presence(presence_msg):
    global persona_at_home, who_is_at_home, how_many_at_home
    global heating_status, heating_standby, heating_overwrite
    
    logging.debug('gestisco il messaggio di presence '+presence_msg)
    
    if len(presence_msg) !=0:
        words = presence_msg.split(' ', 2)
        nome = words[0]
        status = words[1]
        try:
            IFTTTtime = words[2]
            logging.info("IFTTTtime "+IFTTTtime)
            orario = time.strptime(IFTTTtime, "%B %d, %Y at %I:%M%p")
            logging.info("orario letto da mail "+time.asctime(orario))
        except:
            e = sys.exc_info()[0]
            logging.error( "<p>Error: %s</p>" % e )
            orario = time.localtime(time.time())
        # scrive la info di presence su file

        localtime = time.asctime( orario )
        ora_minuti = time.strftime("%H:%M", orario)
        filepresence = open("filepresence","a")  #apre il file dei dati in append mode, se il file non esiste lo crea
        filepresence.write(presence_msg+" "+localtime+"\n")  #scrive la info di presence ed il timestam sul file
        filepresence.close()  #chiude il file dei dati e lo salva

        try:
            n=persona.index(nome)
            if status == 'IN':
                if persona_at_home[n] == False:
                    persona_at_home[n] = True
                    bot.sendMessage(CHAT_ID, "Benvenuto a casa "+nome+"\nSono le "+ora_minuti)
                    f = open(persona[n]+"_at_home","w")  #apre il file dei dati in write mode, se il file non esiste lo crea
                    f.write("IN")  #scrive la info di presence sul file
                    f.close()  #chiude il file dei dati e lo salva
            elif status == 'OUT':
                if persona_at_home[n]:
                    persona_at_home[n] = False
                    bot.sendMessage(CHAT_ID, "Arrivederci a presto "+nome+"\nSono le "+ora_minuti)
                    f = open(persona[n]+"_at_home","w")  #apre il file dei dati in write mode, se il file non esiste lo crea
                    f.write("OUT")  #scrive la info di presence sul file
                    f.close()  #chiude il file dei dati e lo salva
        except ValueError: #non ho riconosciuto la persona
            bot.sendMessage(CHAT_ID, "Padrone verifica se ci sono sconosciuti in casa!")
    
    # calcola chi e' a casa
    who_is_at_home=""
    how_many_at_home=0
    for n in range(persone_della_casa):
        if persona_at_home[n]:
            who_is_at_home+=persona[n]+" "
            how_many_at_home+=1
    if how_many_at_home == 0: #nessuno in casa
        if heating_standby == False:  #standby termosifoni non attivo
            heating_standby = True
            f = open("heating_standby","w")
            f.write('ON')
            f.close()  #chiude il file dei dati e lo salva
            if not heating_overwrite and heating_status: #se termosifoni attivi
                TurnOffHeating()
                #GPIO.output(HEAT_PIN, HEAT_OFF) # spenge i termosifoni
                bot.sendMessage(CHAT_ID, "Ho messo in stand by il riscaldamento in attesa che rientri qualcuno a casa")
    else: #almeno una persona in casa
        if heating_standby: #se standby attivo
            heating_standby = False
            f = open("heating_standby","w")
            f.write('OFF')
            f.close()  #chiude il file dei dati e lo salva
            if not heating_overwrite and heating_status: #se termosifoni attivi prima dello standby
                TurnOnHeating()
                #GPIO.output(HEAT_PIN, HEAT_ON) # riaccende i termosifoni
                bot.sendMessage(CHAT_ID, "Ho riavviato il riscaldamento per il tuo confort, Padrone")
    #return set_presence            

######################## check presence con ping IP su wifi
def check_presence_IP():
    global personaIP, persona_at_home, persone_della_casa
    for n in range(persone_della_casa):
        result = os.system("ping -c 1 " + persona_IP[n])
        if (result == 0):
            if not persona_at_home[n]:
                set_presence(persona[n]+' IN') #richiama la funzione per la gestisce della presence
        else:
            if persona_at_home[n]:
                set_presence(persona[n]+' OUT') #richiama la funzione per la gestisce della presence
####################################################

############# controlla la presence con ping BT #################        
def check_presence_BT():
    global persona_BT, persona_at_home, persone_della_casa
    for n in range (persone_della_casa):
        result = bluetooth.lookup_name(persona_BT[n], timeout=5)
        if (result != None):
            if not persona_at_home[0]:
                set_presence(persona[n]+' IN') #richiama la funzione per la gestisce della presence
        else:
            if persona_at_home[0]:
                set_presence(persona[n]+' OUT') #richiama la funzione per la gestisce della presence
###################################################


##### connette o riconnette alla mail ###########
def connect(retries=5, delay=3):
    while True:
        try:
            mail = imaplib.IMAP4_SSL(imap_host)
            mail.login(EMAIL_ID,EMAIL_PASSWD)
            return mail
        except imaplib.IMAP4_SSL.abort:
            if retries > 0:
                retries -= 1
                time.sleep(delay)
            else:
                raise
#################################################

############## gestione del riscaldamento ##################
def TurnOnHeating():
    global heating_status, heating_standby, heating_overwrite, FILEHEATING, CHAT_ID

    heating_status = True #print "HEATING ON "+localtime+"\n"
    f = open("heating_status","w")
    f.write('ON')
    f.close()  #chiude il file dei dati e lo salva
    
    if not heating_overwrite and heating_standby:
       bot.sendMessage(CHAT_ID, "Fa un po' freddo, Padrone, ma solo solo a casa e faccio un po' di economia")
    else:
        GPIO.output(HEAT_PIN, HEAT_ON) # sets port 0 to 1 (3.3V, on) per accendere i termosifoni
        bot.sendMessage(CHAT_ID, "Accendo il riscaldamento, Padrone")
        orario = time.localtime(time.time())
        localtime = time.asctime( orario )
        ora_minuti = time.strftime("%H:%M", orario)
        fileheating = open(FILEHEATING,"a")  #apre il file dei dati in append mode, se il file non esiste lo crea
        fileheating.write("ON,"+localtime+"\n")  #scrive la info di accensione del riscaldamento il timestamp su file
        fileheating.close()  #chiude il file dei dati e lo salva

    
    
def TurnOffHeating():
    global heating_status, heating_standby, heating_overwrite, FILEHEATING, CHAT_ID
    heating_status = False
    f = open("heating_status","w")
    f.write('OFF')
    f.close()  #chiude il file dei dati e lo salva
    
    GPIO.output(HEAT_PIN, HEAT_OFF) # sets port 0 to 0 (0V, off) per spegnere i termosifoni
    bot.sendMessage(CHAT_ID, "Spengo il riscaldamento, Padrone")
    orario = time.localtime(time.time())
    localtime = time.asctime( orario )
    ora_minuti = time.strftime("%H:%M", orario)
    fileheating = open(FILEHEATING,"a")  #apre il file dei dati in append mode, se il file non esiste lo crea
    fileheating.write("OFF,"+localtime+"\n")  #scrive la info di accensione del riscaldamento il timestamp su file
    fileheating.close()  #chiude il file dei dati e lo salva


##################### inizio gestione presence via email ################
#connect to gmail
def read_gmail():
    global mail
    logging.debug('leggo mail')
    
    try:
        mail.select('inbox')
        mail.list()
        # Any Emails? 
        n=0
        (retcode, messages) = mail.search(None, '(UNSEEN)')
        if retcode == 'OK':
            for num in messages[0].split() :
                logging.info('Processing new emails...')
                n=n+1
                typ, data = mail.fetch(num,'(RFC822)')
                for response_part in data:
                    if isinstance(response_part, tuple):
                        original = email.message_from_string(response_part[1])
                        subject_text=str(original['Subject'])
                        set_presence(subject_text) #richiama la funzione per la gestisce della presence
                        typ, data = mail.store(num,'+FLAGS','\\Seen') #segna la mail come letta
                logging.info("Ho gestito "+str(n)+" messaggi di presence")
    except:
        logging.debug('Errore nella lettura della mail')
        mail = connect()

############################### fine gestione presence via email #######################

############################ TEST Internet connection #############
import socket
REMOTE_SERVER = "www.google.com"
def is_connected():
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

#inizio programma
######## legge da file lo stato di presenza delle persone della casa ###########
for n in range(persone_della_casa):
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

######## legge da file lo programmazione del cronotermostato ###########
initialize_schedule()

######## inizializza il bot Telegram ###########
bot = telepot.Bot(TOKEN)
bot.notifyOnMessage(handle)
logging.info("Listening ...")

help_or_gate = '/help'
if GATE_PRESENT:
    help_or_gate = '/apri'

show_keyboard = {'keyboard': [['/now','/casa'], ['/ho_caldo','/ho_freddo'],['/pulizie',help_or_gate]]} #tastiera personalizzata
bot.sendMessage(CHAT_ID, 'Mi sono appena svegliato, Padrone')

if heating_status and not heating_standby:
    TurnOnHeating()
    #GPIO.output(HEAT_PIN, HEAT_ON) # sets port 0 to 0 (3.3V, off) per spengere i termosifoni
    bot.sendMessage(CHAT_ID, "Rispristino il riscaldamento, Padrone")
else:
    TurnOffHeating()
    #GPIO.output(HEAT_PIN, HEAT_OFF)

GPIO.output(GATE_PIN, GATE_OFF) #pulisce il circuito di apertura cancello

bot.sendMessage(CHAT_ID, 'Come ti posso aiutare?', reply_markup=show_keyboard)

#predispone la tastiera per i visitatori della casa
if GATE_PRESENT:
    show_keyboard = {'keyboard': [['/apri']], 'resize_keyboard':True} #tastiera personalizzata
    bot.sendMessage(CHAT_ID_GATE, "Premere /apri per aprire il cancello", reply_markup=show_keyboard)

mail = connect() #apre la casella di posta

while True:
    now = time.time()
    localtime = time.asctime( time.localtime(now) )
    CurTargetTemp=current_target_temp()
    CurTemp = read_temp()
    CurTempDHT, CurHumidity = read_TandH()
    if CurHumidity == None:
        CurHumidity = 'N.A.'
    if not heating_overwrite:
        if pulizie_status:
            if now >= pulizie_timer:
                pulizie_status=False
                bot.sendMessage(CHAT_ID, "E' terminato il periodo per le pulizie, Padrone")
        else:
            if not heating_status:
                if CurTemp < (CurTargetTemp - 0.2):
                    TurnOnHeating()
            else:
                if CurTemp > (CurTargetTemp + 0.2):
                    TurnOffHeating()
    if report_interval is not None and last_report is not None and now - last_report >= report_interval:
        #apre il file dei dati in append mode, se il file non esiste lo crea
        filedati = open("filedati","a")
        #scrive la temperatura coreente ed il timestam sul file
        filedati.write("T="+str(CurTemp)+",HR="+str(CurHumidity)+"@"+localtime+"\n")
        #chiude il file dei dati e lo salva
        filedati.close()
        
        last_report = now
    # verifica se ci sono nuovi aggiornamenti sulla presence (via email)
    if is_connected():
        read_gmail()
            
    #check_presence_BT()
    if IP_PRESENCE:
        check_presence_IP() # controlla la presente con ping IP
        
    time.sleep(60)

