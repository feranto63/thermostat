#!/usr/bin/python

# DEFINIZIONE VARIABILI DI PERSONALIZZAZIONE
import sys

import logging
# import telegram
# from telegram.error import NetworkError, Unauthorized
from time import sleep
# from telegram.ext import Updater, CommandHandler, MessageHandler, Filters


#PROPRIETARIO = sys.argv[1]  # get user from command-line
owner_found = False


from backports import configparser
#import ConfigParser

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

########### legge da file il token del Telegram Bot e della chat id

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

bot = telepot.Bot(TOKEN)
#bot = telegram.Bot(TOKEN)

#updater = Updater(TOKEN)
#updater = Updater(TOKEN, workers=2)

# Get the dispatcher to register handlers
# dp = updater.dispatcher

#dp.addTelegramCommandHandler("now", handle)
#bot.message_loop(handle)
#bot.telegram.ext.handler(handle)

#logging.info("Listening ...")

bot = telepot.Bot(TOKEN)
bot.message_loop(handle)

update_queue = updater.start_polling(poll_interval=1, timeout=5)

print ("Listening ...")


main_show_keyboard = {'keyboard': [['/now']]} #tastiera personalizzata
bot.sendMessage(CHAT_ID, 'Mi sono appena svegliato, Padrone', disable_notification=debug_notify)


bot.sendMessage(CHAT_ID, 'Come ti posso aiutare?', reply_markup=main_show_keyboard, disable_notification=debug_notify)


while True:
    now = time.time()
    #localtime = time.asctime( time.localtime(now) )
    localtime = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    print(str(localtime))
    #check_presence_BT()
    time.sleep(60)
