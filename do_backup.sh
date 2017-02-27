#!/bin/bash
#  https://www.raspberrypi.org/forums/viewtopic.php?f=36&t=75065

NOMEMAGGIORDOMO="Ambrogio"
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
FTPNAME = "feranto63"
FTPPASS = "cldbzz00"
ncftpput -u $FTPNAME -p $FTPPASS $SERVER /maggiordomo/$NOMEMAGGIORDOMO/ /home/pi/git/thermostat/thermostat/*.*
ncftpput -u $FTPNAME -p $FTPPASS $SERVER /maggiordomo/$NOMEMAGGIORDOMO/ /var/www/templog.db
ncftpput -u $FTPNAME -p $FTPPASS $SERVER /maggiordomo/$NOMEMAGGIORDOMO/ /usr/lib/cgi-bin/webgui.py
ncftpput -u $FTPNAME -p $FTPPASS $SERVER /maggiordomo/$NOMEMAGGIORDOMO/ /etc/supervisor/conf.d/*.*
ncftpput -u $FTPNAME -p $FTPPASS $SERVER /maggiordomo/$NOMEMAGGIORDOMO/ /etc/lirc/lircd.conf
