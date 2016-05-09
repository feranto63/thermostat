
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

i=1
while True:
    if GPIO.input(27):
        pin1 = "ON "
    else:
        pin1 = "OFF"
    if GPIO.input(23):
        pin2 = "ON "
    else:
        pin2 = "OFF"
    if GPIO.input(24):
        pin3 = "ON "
    else:
        pin3 = "OFF"
    if GPIO.input(25):
        pin4 = "ON "
    else:
        pin4 = "OFF"

    print str(i)+"  "+str(pin1)+" - "+str(pin2)+" - "+str(pin3)+" - "+str(pin4)
    time.sleep(1)
    i=i+1
    
#    loop.run_forever()
