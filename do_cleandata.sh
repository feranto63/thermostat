#!/bin/bash
#  https://www.raspberrypi.org/forums/viewtopic.php?f=36&t=75065

# read NOMEMAGGIORDOMO < /home/pi/git/thermostat/thermostat/Maggiordomo.ID

#SERVER="ftp.feranto63.altervista.org"         # IP of Network disk, used for: ftp mail scp

TIMESTAMP=`/bin/date +%Y%m%d%H%M%S`

## BACKUP DATABASE
#BACKUPFILE="maggiordomo_$TIMESTAMP.db" # backups will be named "domoticz_YYYYMMDDHHMMSS.db.gz"
#BACKUPFILEGZ="$BACKUPFILE".gz

## BACKUP SCRIPTS

#BACKUPFILEDIR="maggiordomo_all_$TIMESTAMP.tar.gz"

### Create backup and ZIP it
## ----->>>> NON SERVE IL COMANDO CURL PERCHE' I FILE SONO IN LOCALE

## /usr/bin/curl -s http://$DOMO_IP:$DOMO_PORT/backupdatabase.php > /tmp/$BACKUPFILE
# gzip -9 /tmp/$BACKUPFILE
##Back domoticz folder incl database
#tar -zcvf /tmp/$BACKUPFILEDIR /home/pi/git/thermostat/thermostat/

### Send to Network disk through SCP
#FTPNAME="feranto63"
#FTPPASS="cldbzz00"
sudo rm /home/pi/git/thermostat/thermostat/chatid
sudo rm /pi/git/thermostat/thermostat/filedati
sudo rm /home/pi/git/thermostat/thermostat/fileheating
sudo rm /home/pi/git/thermostat/thermostat/filepresence
sudo rm /home/pi/git/thermostat/thermostat/heating_standby
sudo rm /home/pi/git/thermostat/thermostat/heating_status
sudo rm /home/pi/git/thermostat/thermostat/heating_update
sudo rm /home/pi/git/thermostat/thermostat/MAGGIORDOMO.jpg
sudo rm /home/pi/git/thermostat/thermostat/termostato.log
sudo rm /home/pi/git/thermostat/thermostat/thermogram2.ini
sudo rm /home/pi/git/thermostat/thermostat/termoschedule
sudo rm /home/pi/git/thermostat/thermostat/token
sudo rm /home/pi/git/thermostat/thermostat/Maggiordomo.ID
sudo rm /home/pi/git/thermostat/thermostat/chatid_cancello
sudo rm /var/www/templog.db
sudo rm /usr/lib/cgi-bin/webgui.py
sudo rm /etc/supervisor/conf.d/*.conf
sudo rm /etc/lirc/lircd.conf
