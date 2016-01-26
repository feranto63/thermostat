
#imports for thermometer reading
import os
import glob
import time
#imports for gmail reading
import imaplib
import email
#import for Telegram API
import sys
import pprint
import telepot

###################### gestisce i comandi inviati al Telegram Bot
def handle(msg):
    global last_report, report_interval #parametri per il monitoraggio su file delle temperature
    global heating_status               #stato di accensione dei termosifoni

    msg_type, chat_type, chat_id = telepot.glance2(msg)

    # ignore non-text message
    if msg_type != 'text':
        return

    command = msg['text'].strip().lower()
    CurTemp = read_temp()

    if command == '/now':
        bot.sendMessage(chat_id, "La temperatura misurata e' di "+str("%0.1f" % CurTemp)+" C, Padrone")
    elif command == '/5m':
        bot.sendMessage(chat_id, "Avvio il monitoraggio ogni 5 minuti, Padrone")
        last_report = time.time()
        report_interval = 300    # report every 60 seconds
    elif command == '/1h':
        bot.sendMessage(chat_id, "Avvio il monitoraggio ogni ora, Padrone")
        last_report = time.time()
        report_interval = 3600  # report every 3600 seconds
    elif command == '/annulla':
        last_report = None
        report_interval = None  # clear periodic reporting
        bot.sendMessage(chat_id, "Certamente, Padrone")
    elif command == '/ho_freddo':
        if heating_status:
            bot.sendMessage(chat_id, "Sto facendo del mio meglio, Padrone")
        else:
            GPIO.output(17, 1) # sets port 0 to 1 (3.3V, on) per accendere i termosifoni
            #print "HEATING ON "+localtime+"\n"
            bot.sendMessage(chat_id, "Accendo il riscaldamento, Padrone")
    elif command == '/ho_caldo':
        if heating_status:
            GPIO.output(17, 0) # sets port 0 to 0 (3.3V, off) per spengere i termosifoni
            #print "HEATING OFF "+localtime+"\n"
            bot.sendMessage(chat_id, "Spengo il riscaldamento, Padrone")
        else:      
            bot.sendMessage(chat_id, "Dovresti aprire le finestre, Padrone")

    else:
        bot.sendMessage(chat_id, "Puoi ripetere, Padrone? I miei circuiti sono un po' arrugginiti")



############ legge da file il token del Telegram Bot e della chat id
import logging

tokenpath = os.path.dirname(os.path.realpath(__file__)) + "/token"
chatidpath = os.path.dirname(os.path.realpath(__file__)) + "/chatid"

logging.basicConfig( level=logging.INFO)

import requests

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
    
    #-94452612 # magic number: chat_id del gruppo termostato antonelli
        

# variables for periodic reporting
last_report = None
report_interval = None

# variable for heating status
heating_status = False

bot = telepot.Bot(TOKEN)
bot.notifyOnMessage(handle)
logging.info("Listening ...")

################# gestione della interfaccia di GPIO   
# wiringpi numbers  
import RPi.GPIO as GPIO
##import wiringpi2 as wiringpi
##wiringpi.wiringPiSetup()
##wiringpi.pinMode(0, 1) # sets WP pin 0 to output
GPIO.setmode(GPIO.BCM)
GPIO.setup(17,GPIO.OUT)

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

##################### funzione per la gestione dei messaggi di presence
def set_presence(presence_msg):
    


##################### inizio gestione presence via email ################
#connect to gmail
def read_gmail():
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.login('MaggiordomoBot@gmail.com','cldbzz00') #login e password da mettere su file successivamente
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

                    logging.info(original['From'])
                    logging.info (original['Subject'])
                    set_presence(original['Subject']) #richiama la funzione per la gestisce della presence
                    
                    typ, data = mail.store(num,'+FLAGS','\\Seen') #segna la mail come letta

        logging.info("Ho gestito "+str(n)+" messaggi di presence")
    
############################### fine gestione presence via email #######################


#inizio programma
bot.sendMessage(CHAT_ID, 'Mi sono appena svegliato, Padrone')

while True:
        # Is it time to report again?
        now = time.time()
        localtime = time.asctime( time.localtime(now) )
        if report_interval is not None and last_report is not None and now - last_report >= report_interval:
            CurTemp = read_temp()
            #apre il file dei dati in append mode, se il file non esiste lo crea
            filedati = open("filedati","a")
            #scrive la temperatura coreente ed il timestam sul file
            filedati.write(str(CurTemp)+"@"+localtime+"\n")
            #chiude il file dei dati e lo salva
            filedati.close()
            
            last_report = now
        # verifica se ci sono nuovi aggiornamenti sulla presence (via email)
        read_gmail()
        time.sleep(60)

    
    #if (Tdes > CurTemp):#Compare varSubject to temp
    #    GPIO.output(17, 1) # sets port 0 to 1 (3.3V, on)
    #    print "HEATING ON "+localtime+"\n"
    #    bot.sendMessage("HEATING ON @ "+localtime)
    #else:
    #    GPIO.output(17, 0) # sets port 0 to 0 (3.3V, off)
    #    print "HEATING OFF "+localtime+"\n"
    #    bot.sendMessage("HEATING OFF @ "+localtime)
    #    time.sleep(300) #wait 5 minutes
    # manda un telegram con la temperatura ogni 12 x 5 minuti = 1 ora
    #bot.sendMessage(CHAT_ID, "La temperatura misurata e' di "+str(CurTemp)+" C, Padrone")
