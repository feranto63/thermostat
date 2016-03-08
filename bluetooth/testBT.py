#!/usr/bin/python
import bluetooth
import time

FerIN = 0
FerOUT = 0

print "In/Out Board"

while True:
  print "Buscando " + time.strftime("%a, %d %b %Y %H:%M:%S", time.gmtime())
  result = bluetooth.lookup_name('F0:5B:7B:43:42:68', timeout=5)
  if (result != None):
    print "Fer: in"
  if FerIN == 0:
    FerIN = FerIN + 1
    #import subprocess
    #subprocess.call(['bash','/home/pi/alarma_apaga.sh'])
    #subprocess.call(['bash','/home/pi/textoAvoz.sh','Bienvenido a casa Hector'])
    FerOUT = 0
    time.sleep(300)
  else:
    print "Fer: out"
    FerIN = 0
    FerOUT = FerOUT + 1
print "Fer IN:"
print FerIN
print "FerOUT"
print FerOUT
print "------"
