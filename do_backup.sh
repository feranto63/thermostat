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
read FTPNAME < /home/pi/git/thermostat/thermostat/FTPNAME
read FTPPASS < /home/pi/git/thermostat/thermostat/FTPPASS

ncftpput -u $FTPNAME -p $FTPPASS $SERVER /maggiordomo/$NOMEMAGGIORDOMO/ /home/pi/git/thermostat/thermostat/chatid
ncftpput -u $FTPNAME -p $FTPPASS $SERVER /maggiordomo/$NOMEMAGGIORDOMO/ /home/pi/git/thermostat/thermostat/filedati
ncftpput -u $FTPNAME -p $FTPPASS $SERVER /maggiordomo/$NOMEMAGGIORDOMO/ /home/pi/git/thermostat/thermostat/fileheating
ncftpput -u $FTPNAME -p $FTPPASS $SERVER /maggiordomo/$NOMEMAGGIORDOMO/ /home/pi/git/thermostat/thermostat/filepresence
ncftpput -u $FTPNAME -p $FTPPASS $SERVER /maggiordomo/$NOMEMAGGIORDOMO/ /home/pi/git/thermostat/thermostat/heating_standby
ncftpput -u $FTPNAME -p $FTPPASS $SERVER /maggiordomo/$NOMEMAGGIORDOMO/ /home/pi/git/thermostat/thermostat/heating_status
ncftpput -u $FTPNAME -p $FTPPASS $SERVER /maggiordomo/$NOMEMAGGIORDOMO/ /home/pi/git/thermostat/thermostat/heating_update
ncftpput -u $FTPNAME -p $FTPPASS $SERVER /maggiordomo/$NOMEMAGGIORDOMO/ /home/pi/git/thermostat/thermostat/MAGGIORDOMO.jpg
ncftpput -u $FTPNAME -p $FTPPASS $SERVER /maggiordomo/$NOMEMAGGIORDOMO/ /home/pi/git/thermostat/thermostat/termostato.log
ncftpput -u $FTPNAME -p $FTPPASS $SERVER /maggiordomo/$NOMEMAGGIORDOMO/ /home/pi/git/thermostat/thermostat/thermogram2.ini
ncftpput -u $FTPNAME -p $FTPPASS $SERVER /maggiordomo/$NOMEMAGGIORDOMO/ /home/pi/git/thermostat/thermostat/termoschedule
ncftpput -u $FTPNAME -p $FTPPASS $SERVER /maggiordomo/$NOMEMAGGIORDOMO/ /home/pi/git/thermostat/thermostat/token
ncftpput -u $FTPNAME -p $FTPPASS $SERVER /maggiordomo/$NOMEMAGGIORDOMO/ /home/pi/git/thermostat/thermostat/Maggiordomo.ID
ncftpput -u $FTPNAME -p $FTPPASS $SERVER /maggiordomo/$NOMEMAGGIORDOMO/ /home/pi/git/thermostat/thermostat/chatid_cancello
ncftpput -u $FTPNAME -p $FTPPASS $SERVER /maggiordomo/$NOMEMAGGIORDOMO/ /home/pi/git/thermostat/thermostat/BotAssistant.token
ncftpput -u $FTPNAME -p $FTPPASS $SERVER /maggiordomo/$NOMEMAGGIORDOMO/ /home/pi/git/thermostat/thermostat/BotAssistant.chatid
ncftpput -u $FTPNAME -p $FTPPASS $SERVER /maggiordomo/$NOMEMAGGIORDOMO/ /var/www/templog.db
ncftpput -u $FTPNAME -p $FTPPASS $SERVER /maggiordomo/$NOMEMAGGIORDOMO/ /usr/lib/cgi-bin/webgui.py
ncftpput -u $FTPNAME -p $FTPPASS $SERVER /maggiordomo/$NOMEMAGGIORDOMO/ /etc/supervisor/conf.d/*.*
ncftpput -u $FTPNAME -p $FTPPASS $SERVER /maggiordomo/$NOMEMAGGIORDOMO/ /etc/lirc/lircd.conf
sudo rm /home/pi/git/thermostat/thermostat/termostato.log



