
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



################# gestione della interfaccia di GPIO   
# wiringpi numbers  
import RPi.GPIO as GPIO
##import wiringpi2 as wiringpi
##wiringpi.wiringPiSetup()
##wiringpi.pinMode(0, 1) # sets WP pin 0 to output
GPIO.setmode(GPIO.BCM)
GPIO.setup(27,GPIO.IN)
GPIO.setup(23,GPIO.IN)
GPIO.setup(24,GPIO.IN)
GPIO.setup(25,GPIO.IN)


while True:
    pin1 = GPIO.input(27)
    pin2 = GPIO.input(23)
    pin3 = GPIO.input(24)
    pin4 = GPIO.input(25)
    
    print str(pin1)+" - "+str(pin2)+" - "+str(pin3)+" - "+str(pin4)
    time.sleep(1)
    
#    loop.run_forever()
