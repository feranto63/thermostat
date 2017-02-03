#!/bin/bash
#  https://www.raspberrypi.org/forums/viewtopic.php?f=36&t=75065

NOMEMAGGIORDOMO="Ambrogio"
## LOCAL/FTP/SCP/MAIL PARAMETERS
SERVER="http://ftp.feranto63.altervista.org/"         # IP of Network disk, used for: ftp mail scp
#DOMO_IP="192.168.5.75"    # Domoticz IP used for all
#DOMO_PORT="8080"            # Domoticz port used for all
## END OF USER CONFIGURABLE PARAMETERS

TIMESTAMP=`/bin/date +%Y%m%d%H%M%S`

## BACKUP DATABASE
BACKUPFILE="maggiordomo_$TIMESTAMP.db" # backups will be named "domoticz_YYYYMMDDHHMMSS.db.gz"
BACKUPFILEGZ="$BACKUPFILE".gz

## BACKUP SCRIPTS

BACKUPFILEDIR="maggiordomo_all_$TIMESTAMP.tar.gz"

### Create backup and ZIP it
## ----->>>> NON SERVE IL COMANDO CURL PERCHE' I FILE SONO IN LOCALE

## /usr/bin/curl -s http://$DOMO_IP:$DOMO_PORT/backupdatabase.php > /tmp/$BACKUPFILE
# gzip -9 /tmp/$BACKUPFILE
##Back domoticz folder incl database
tar -zcvf /tmp/$BACKUPFILEDIR /home/pi/git/thermostat/thermostat/

### Send to Network disk through SCP
# curl -u ftpuser:ftppass -T myfile.txt ftp://ftp.testserver.com
# scp /tmp/$BACKUPFILEGZ pi@$SERVER:/maggiordomo/$NOMEMAGGIORDOMO/
scp /tmp/$BACKUPFILEDIR  pi@$SERVER:/maggiordomo/$NOMEMAGGIORDOMO/

### Remove temp backup files
# /bin/rm /tmp/$BACKUPFILEGZ
/bin/rm /tmp/$BACKUPFILEDIR

### Done!
