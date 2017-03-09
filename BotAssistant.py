import sys
import time
import telepot

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
        filename='/home/pi/BotAssistant.log',
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.WARN)



"""
$ python2.7 skeleton.py <token>
A skeleton for your telepot programs.
"""
############ legge da file il token del Telegram Bot e della chat id

tokenpath = os.path.dirname(os.path.realpath(__file__)) + "/BotAssistant.token"
IDpath= os.path.dirname(os.path.realpath(__file__)) + "/Maggiordomo.ID"
#chatidpath = os.path.dirname(os.path.realpath(__file__)) + "/chatid"
#chatidgatepath = os.path.dirname(os.path.realpath(__file__)) + "/chatid_cancello"


try:
    tokenFile = open(tokenpath,'r')
    TOKEN = tokenFile.read().strip()
    tokenFile.close()
except IOError: 
    logging.error("Non ho trovato il file di token. E' necessario creare un file 'token' con la token telegram per il bot. In ogni caso questo file NON deve essere tracciato da git - viene ignorato perche' menzionato nel .gitignore.")
    exit()

logging.info("caricata token.")

def handle(msg):
    flavor = telepot.flavor(msg)

    summary = telepot.glance(msg, flavor=flavor)
    print flavor, summary


bot = telepot.Bot(TOKEN)
bot.message_loop(handle)
print 'Listening ...'

# generate a name for this maggiordomo if does not exist
try:
    MaggiordomoIDFile = open(IDpath,'r')
    MaggiordomoID = MaggiordomoIDFile.read().strip()
    MaggiordomoIDFile.close()
    bot.sendmessage("sono "+MaggiordomoID+". Mi sono appena svegliato")

except IOError: 
    logging.error("Non ho trovato il file con ID del maggiordomo. Genero ID e lo salvo")
    MaggiordomoID = "maggiordomo.1234" #da generare in modo random
    MaggiordomoIDFile = open(IDpath,'w')
    MaggiordomoIDFile.write(MaggiordomoID)
    MaggiordomoIDFile.close()

    bot.sendmessage("sono "+MaggiordomoID+". Sono stato appena generato")


# Keep the program running.
while 1:
    time.sleep(10)
