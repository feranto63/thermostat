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
#bot.message_loop(handle)
print 'running Bot Assistant ...'

# myIPaddress = str(subprocess.check_output(['dig','+short','myip.opendns.com','@resolver1.opendns.com']))
myIPaddress = str(subprocess.check_output(['hostname','I']))

# generate a name for this maggiordomo if does not exist
try:
    MaggiordomoIDFile = open(IDpath,'r')
    MaggiordomoID = MaggiordomoIDFile.read().strip()
    MaggiordomoIDFile.close()
    bot.sendMessage(CHATID, "sono "+MaggiordomoID+". Mi sono appena svegliato", disable_notification=True)

except IOError: 
    logging.error("Non ho trovato il file con ID del maggiordomo. Genero ID e lo salvo")
    MaggiordomoID = "Maggiordomo-"+''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(10)) #da generare in modo random
    MaggiordomoIDFile = open(IDpath,'w')
    MaggiordomoIDFile.write(MaggiordomoID)
    MaggiordomoIDFile.close()

    bot.sendMessage(CHATID,"sono "+MaggiordomoID+". Sono stato appena generato", disable_notification=True)

bot.sendMessage(CHATID,"il mio indirizzo IP e' "+myIPaddress, disable_notification=True)

# Keep the program running.
#while 1:
#    time.sleep(10)
