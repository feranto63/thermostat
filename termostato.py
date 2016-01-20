#prima versione del termostato su pi
#flowchart
#ogni 5 minuti leggi la temperatura e lo stato della caldaia
#memorizza i dati sul DB
#grafica lo storico orario
#richiedi in input la temperatura desiderata
#Tdes=raw_input("temperatura desiderata = ")
#print "Tdes=",Tdes
#se Tdes > Tact then turnon caldaia
#loop


#imports for thermometer reading
import os
import glob
import time
#imports for gmail reading
#import imaplib
#import email

import thermogram.thermogram as thermogram
# voglio parlare con il bot MaggiorBot
mybot='@MaggiordomoBot'
bot = thermogram.Bot() #definisce Telegam bot con token in file token e chatid in file chatid


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

#inizio programma
bot.sendMessage("Ho avviato il monitoraggio delle temperature, Padrone")
while True:
    for i in range(1,12):
        localtime = time.asctime( time.localtime(time.time()) )
        #print "Local current time :", localtime
    
        #print "Current temp"
        CurTemp = read_temp()
        #print CurTemp

        #Tdes=input("temperatura desiderata = ")
        #print "Target temp=",Tdes

        #apre il file dei dati in append mode, se il file non esiste lo crea
        filedati = open("filedati","a")

        #scrive la temperatura coreente ed il timestam sul file
        filedati.write(str(CurTemp)+"@"+localtime+"\n")

        #chiude il file dei dati e lo salva
        filedati.close()
    
    #if (Tdes > CurTemp):#Compare varSubject to temp
    #    GPIO.output(17, 1) # sets port 0 to 1 (3.3V, on)
    #    print "HEATING ON "+localtime+"\n"
    #    bot.sendMessage("HEATING ON @ "+localtime)
    #else:
    #    GPIO.output(17, 0) # sets port 0 to 0 (3.3V, off)
    #    print "HEATING OFF "+localtime+"\n"
    #    bot.sendMessage("HEATING OFF @ "+localtime)
        time.sleep(300) #wait 5 minutes
    # manda un telegram con la temperatura ogni 12 x 5 minuti = 1 ora
    bot.sendMessage("La temperatura misurata e' di "+str(CurTemp)+" C, Padrone")
