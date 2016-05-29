#!/usr/bin/python

# DEFINIZIONE VARIABILI DI PERSONALIZZAZIONE
import sys

import logging
import telegram
from telegram.error import NetworkError, Unauthorized
from time import sleep
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters


#PROPRIETARIO = sys.argv[1]  # get user from command-line
owner_found = False


import ConfigParser

settings = ConfigParser.ConfigParser()
settings.read('thermogram2.ini')
persone_della_casa = settings.getint('SectionOne','persone_della_casa')
persona= settings.get('SectionOne','persona').split("\n")
#persona_at_home=settings.getboolean('SectionOne','persona_at_home').split("\n")
persona_at_home=[True, True, True, True, True, True, True, True, True]
imap_host = settings.get('SectionOne','imap_host')
EMAIL_ID=settings.get('SectionOne','EMAIL_ID')
EMAIL_PASSWD=settings.get('SectionOne','EMAIL_PASSWD')
persona_IP=settings.get('SectionOne','persona_IP').split("\n")
persona_BT=settings.get('SectionOne','persona_BT').split("\n")
GATE_PRESENT = settings.getboolean('SectionOne','GATE_PRESENT')
IP_PRESENCE = settings.getboolean('SectionOne','IP_PRESENCE')
BT_PRESENCE = settings.getboolean('SectionOne','BT_PRESENCE')
DHT_PRESENCE = settings.getboolean('SectionOne','DHT_PRESENCE')
DS_PRESENCE = settings.getboolean('SectionOne','DS_PRESENCE')
owner_found= settings.getboolean('SectionOne','owner_found')


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
DHT_PIN = 18
dbname='/var/www/templog.db'
hide_notify = False
debug_notify = True

lucchetto_chiuso = u'\U0001f512' # '\xF0\x9F\x94\x92'  #	lock U+1F512
lucchetto_aperto = u'\U0001f513' # '\xF0\x9F\x94\x93'  #    open lock U+1F513	


#imports for thermometer reading
import os
import glob
import time
#imports for gmail reading
#import for Telegram API
# import pprint
import telepot

###################### gestisce i comandi inviati al Telegram Bot
def handle(msg):
    global CHAT_ID

    #msg_type, chat_type, chat_id = telepot.glance(msg)
    msg_sender = msg['from']['first_name']
    
    #if msg_type != 'text':
    #    return

    command = msg['text'].strip().lower()
    
    if command == '/now':
        bot.sendMessage(CHAT_ID, 'ho ricevuto il comando now')
    else:
        bot.sendMessage(CHAT_ID, "Puoi ripetere, Padrone? I miei circuiti sono un po' arrugginiti")

TOKEN = '186703015:AAEJ2qKIPwbhktlPF0qdfLWHFJFSlE3uhBc'
CHAT_ID = 26228522


def set_presence(n, presence_msg):
    global persona_at_home, who_is_at_home, how_many_at_home, hide_notify
    global CHAT_ID
    global debug_notify
    

    if len(presence_msg) !=0:
        words = presence_msg.split(' ', 2)
        nome = words[0]
        status = words[1]
        orario = time.localtime(time.time())
        # scrive la info di presence su file

        localtime = time.asctime( orario )
        ora_minuti = time.strftime("%H:%M", orario)
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
                bot.sendMessage(CHAT_ID, messaggio_IN_OUT ,disable_notification=hide_notify)
        elif status == 'OUT':
            if persona_at_home[n]:
                persona_at_home[n] = False
                messaggio_IN_OUT="Arrivederci a presto "+nome+"\nSono le "+ora_minuti
                changed = True
                bot.sendMessage(CHAT_ID, messaggio_IN_OUT ,disable_notification=hide_notify)
    return changed, messaggio_IN_OUT
    #return set_presence            


######################## check presence con ping IP su wifi
import subprocess

def check_presence_IP():
    global personaIP, persona_at_home, persone_della_casa
    global CHAT_ID
    for n in range(persone_della_casa):
#        result = os.system("ping -c 2 " + persona_IP[n])
        result = subprocess.call(['ping','-c','1',persona_IP[n]])
        if (result == 0):
            if not persona_at_home[n]:
                changed, messaggio_IN_OUT= set_presence(n, persona[n]+' IN') #richiama la funzione per la gestisce della presence
#                if changed:
#                    bot.sendMessage(CHAT_ID, messaggio_IN_OUT)
        else:
            if persona_at_home[n]:
                changed, messaggio_IN_OUT= set_presence(n, persona[n]+' OUT') #richiama la funzione per la gestisce della presence
#                if changed:
#                    bot.sendMessage(CHAT_ID, messaggio_IN_OUT)

####################################################




############ legge da file lo stato delle persone della casa ###############
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

######## inizializza il bot Telegram ###########
<<<<<<< HEAD
#bot = telepot.Bot(TOKEN)
bot = telegram.Bot(TOKEN)

updater = Updater(bot)
#updater = Updater(TOKEN, workers=2)

# Get the dispatcher to register handlers
dp = updater.dispatcher

dp.addTelegramCommandHandler("now", handle)
#bot.message_loop(handle)
#bot.telegram.ext.handler(handle)

logging.info("Listening ...")
=======
bot = telepot.Bot(TOKEN)
bot.message_loop(handle)
print "Listening ..."
>>>>>>> origin/master


main_show_keyboard = {'keyboard': [['/now']]} #tastiera personalizzata
bot.sendMessage(CHAT_ID, 'Mi sono appena svegliato, Padrone', disable_notification=debug_notify)


bot.sendMessage(CHAT_ID, 'Come ti posso aiutare?', reply_markup=main_show_keyboard, disable_notification=debug_notify)


while True:
    now = time.time()
    #localtime = time.asctime( time.localtime(now) )
    localtime = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    #check_presence_BT()
    if IP_PRESENCE:
        check_presence_IP() # controlla la presente con ping IP
    time.sleep(60)
