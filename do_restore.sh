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

mv /home/pi/git/thermostat/thermostat/chatid /home/pi/git/thermostat/thermostat/old_chatid
ncftpget -C -u $FTPNAME -p $FTPPASS $SERVER /maggiordomo/$NOMEMAGGIORDOMO/chatid /home/pi/git/thermostat/thermostat/chatid
ncftpget -C -u $FTPNAME -p $FTPPASS $SERVER /maggiordomo/$NOMEMAGGIORDOMO/filedati /home/pi/git/thermostat/thermostat/filedati
ncftpget -C -u $FTPNAME -p $FTPPASS $SERVER /maggiordomo/$NOMEMAGGIORDOMO/fileheating /home/pi/git/thermostat/thermostat/fileheating
ncftpget -C -u $FTPNAME -p $FTPPASS $SERVER /maggiordomo/$NOMEMAGGIORDOMO/filepresence /home/pi/git/thermostat/thermostat/filepresence
ncftpget -C -u $FTPNAME -p $FTPPASS $SERVER /maggiordomo/$NOMEMAGGIORDOMO/heating_standby /home/pi/git/thermostat/thermostat/heating_standby
ncftpget -C -u $FTPNAME -p $FTPPASS $SERVER /maggiordomo/$NOMEMAGGIORDOMO/heating_status /home/pi/git/thermostat/thermostat/heating_status
ncftpget -C -u $FTPNAME -p $FTPPASS $SERVER /maggiordomo/$NOMEMAGGIORDOMO/heating_update /home/pi/git/thermostat/thermostat/heating_update
ncftpget -C -u $FTPNAME -p $FTPPASS $SERVER /maggiordomo/$NOMEMAGGIORDOMO/MAGGIORDOMO.jpg /home/pi/git/thermostat/thermostat/MAGGIORDOMO.jpg
#ncftpget -C -u $FTPNAME -p $FTPPASS $SERVER /maggiordomo/$NOMEMAGGIORDOMO/termostato.log /home/pi/git/thermostat/thermostat/termostato.log
mv /home/pi/git/thermostat/thermostat/thermogram2.ini /home/pi/git/thermostat/thermostat/old_thermogram2.ini
ncftpget -C -u $FTPNAME -p $FTPPASS $SERVER /maggiordomo/$NOMEMAGGIORDOMO/thermogram2.ini /home/pi/git/thermostat/thermostat/thermogram2.ini
ncftpget -C -u $FTPNAME -p $FTPPASS $SERVER /maggiordomo/$NOMEMAGGIORDOMO/thermoschedule /home/pi/git/thermostat/thermostat/termoschedule
mv /home/pi/git/thermostat/thermostat/token /home/pi/git/thermostat/thermostat/old_token
ncftpget -C -u $FTPNAME -p $FTPPASS $SERVER /maggiordomo/$NOMEMAGGIORDOMO/token /home/pi/git/thermostat/thermostat/token
# ncftpput -u $FTPNAME -p $FTPPASS $SERVER /maggiordomo/$NOMEMAGGIORDOMO/ /home/pi/git/thermostat/thermostat/Maggiordomo.ID
mv /home/pi/git/thermostat/thermostat/chatid_cancello /home/pi/git/thermostat/thermostat/old_chatid_cancello
ncftpget -C -u $FTPNAME -p $FTPPASS $SERVER /maggiordomo/$NOMEMAGGIORDOMO/chatid_cancello /home/pi/git/thermostat/thermostat/chatid_cancello
ncftpget -C -u $FTPNAME -p $FTPPASS $SERVER /maggiordomo/$NOMEMAGGIORDOMO/templog.db /var/www/templog.db
ncftpget -C -u $FTPNAME -p $FTPPASS $SERVER /maggiordomo/$NOMEMAGGIORDOMO/webgui.py /usr/lib/cgi-bin/webgui.py
ncftpget -C -u $FTPNAME -p $FTPPASS $SERVER /maggiordomo/$NOMEMAGGIORDOMO/*.conf /etc/supervisor/conf.d/*.conf
ncftpget -C -u $FTPNAME -p $FTPPASS $SERVER /maggiordomo/$NOMEMAGGIORDOMO/lircd.conf /etc/lirc/lircd.conf


