#!/bin/bash
#  https://www.raspberrypi.org/forums/viewtopic.php?f=36&t=75065

read NOMEMAGGIORDOMO < /home/pi/git/thermostat/thermostat/Maggiordomo.ID

SERVER="ftp.feranto63.altervista.org"         # IP of Network disk, used for: ftp mail scp

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
#tar -zcvf /tmp/$BACKUPFILEDIR /home/pi/git/thermostat/thermostat/

### Send to Network disk through SCP
FTPNAME="feranto63"
FTPPASS="cldbzz00"
ncftpget -u $FTPNAME -p $FTPPASS $SERVER /maggiordomo/$NOMEMAGGIORDOMO/ /home/pi/git/thermostat/thermostat/chatid
ncftpget -u $FTPNAME -p $FTPPASS $SERVER /maggiordomo/$NOMEMAGGIORDOMO/ /home/pi/git/thermostat/thermostat/filedati
ncftpget -u $FTPNAME -p $FTPPASS $SERVER /maggiordomo/$NOMEMAGGIORDOMO/ /home/pi/git/thermostat/thermostat/fileheating
ncftpget -u $FTPNAME -p $FTPPASS $SERVER /maggiordomo/$NOMEMAGGIORDOMO/ /home/pi/git/thermostat/thermostat/filepresence
ncftpget -u $FTPNAME -p $FTPPASS $SERVER /maggiordomo/$NOMEMAGGIORDOMO/ /home/pi/git/thermostat/thermostat/heating_standby
ncftpget -u $FTPNAME -p $FTPPASS $SERVER /maggiordomo/$NOMEMAGGIORDOMO/ /home/pi/git/thermostat/thermostat/heating_status
ncftpget -u $FTPNAME -p $FTPPASS $SERVER /maggiordomo/$NOMEMAGGIORDOMO/ /home/pi/git/thermostat/thermostat/heating_update
ncftpget -u $FTPNAME -p $FTPPASS $SERVER /maggiordomo/$NOMEMAGGIORDOMO/ /home/pi/git/thermostat/thermostat/MAGGIORDOMO.jpg
ncftpget -u $FTPNAME -p $FTPPASS $SERVER /maggiordomo/$NOMEMAGGIORDOMO/ /home/pi/git/thermostat/thermostat/termostato.log
ncftpget -u $FTPNAME -p $FTPPASS $SERVER /maggiordomo/$NOMEMAGGIORDOMO/ /home/pi/git/thermostat/thermostat/thermogram2.ini
ncftpget -u $FTPNAME -p $FTPPASS $SERVER /maggiordomo/$NOMEMAGGIORDOMO/ /home/pi/git/thermostat/thermostat/termoschedule
ncftpget -u $FTPNAME -p $FTPPASS $SERVER /maggiordomo/$NOMEMAGGIORDOMO/ /home/pi/git/thermostat/thermostat/token
# ncftpput -u $FTPNAME -p $FTPPASS $SERVER /maggiordomo/$NOMEMAGGIORDOMO/ /home/pi/git/thermostat/thermostat/Maggiordomo.ID
ncftpget -u $FTPNAME -p $FTPPASS $SERVER /maggiordomo/$NOMEMAGGIORDOMO/ /home/pi/git/thermostat/thermostat/chatid_cancello
ncftpget -u $FTPNAME -p $FTPPASS $SERVER /maggiordomo/$NOMEMAGGIORDOMO/ /var/www/templog.db
ncftpget -u $FTPNAME -p $FTPPASS $SERVER /maggiordomo/$NOMEMAGGIORDOMO/ /usr/lib/cgi-bin/webgui.py
ncftpget -u $FTPNAME -p $FTPPASS $SERVER /maggiordomo/$NOMEMAGGIORDOMO/ /etc/supervisor/conf.d/*.*
ncftpget -u $FTPNAME -p $FTPPASS $SERVER /maggiordomo/$NOMEMAGGIORDOMO/ /etc/lirc/lircd.conf
