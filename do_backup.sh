#!/bin/bash

## LOCAL/FTP/SCP/MAIL PARAMETERS
SERVER="192.168.5.10"         # IP of Network disk, used for: ftp mail scp
DOMO_IP="192.168.5.75"    # Domoticz IP used for all
DOMO_PORT="8080"            # Domoticz port used for all
## END OF USER CONFIGURABLE PARAMETERS

TIMESTAMP=`/bin/date +%Y%m%d%H%M%S`

## BACKUP DATABASE
BACKUPFILE="domoticz_$TIMESTAMP.db" # backups will be named "domoticz_YYYYMMDDHHMMSS.db.gz"
BACKUPFILEGZ="$BACKUPFILE".gz

## BACKUP SCRIPTS

BACKUPFILEDIR="domoticz_all_$TIMESTAMP.tar.gz"

### Create backup and ZIP it
/usr/bin/curl -s http://$DOMO_IP:$DOMO_PORT/backupdatabase.php > /tmp/$BACKUPFILE
gzip -9 /tmp/$BACKUPFILE
##Back domoticz folder incl database
tar -zcvf /tmp/$BACKUPFILEDIR /home/pi/domoticz/

### Send to Network disk through SCP
scp /tmp/$BACKUPFILEGZ pi@192.168.5.10:/$SERVER/media/hdd/Domoticz_backup/
scp /tmp/$BACKUPFILEDIR  pi@192.168.5.10:/$SERVER/media/hdd/Domoticz_backup/

### Remove temp backup files
/bin/rm /tmp/$BACKUPFILEGZ
/bin/rm /tmp/$BACKUPFILEDIR

### Done!
