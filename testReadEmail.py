import os
import glob
import time
#imports for gmail reading
import imaplib
import email
#import for Telegram API
import sys
import pprint

##################### inizio gestione mail ################
#connect to gmail
def read_gmail():
    global varSubject
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.login('MaggiordomoBot@gmail.com','cldbzz00')
    mail.select('inbox')
    mail.list()

#    typ, data = mail.search(None, 'ALL')
#    for num in data[0].split():
#        typ, data = mail.fetch(num, '(RFC822)')
#    typ, data = mail.search(None, 'ALL')
#    ids = data[0]
#    id_list = ids.split()

    
# Any Emails? 
    newmails=mail.recent()
    print "nuove mail ="+str(newmails)

    n=0
    (retcode, messages) = mail.search(None, '(UNSEEN)')
    if retcode == 'OK':

        for num in messages[0].split() :
            print 'Processing '
            n=n+1
            typ, data = mail.fetch(num,'(RFC822)')
            for response_part in data:
                if isinstance(response_part, tuple):
                    original = email.message_from_string(response_part[1])

                    print original['From']
                    print original['Subject']
                    typ, data = mail.store(num,'+FLAGS','\\Seen')

        print n
    
# get most recent email id
#    if id_list:
#        latest_email_id = int( id_list[-1] )
#        for i in range( latest_email_id, latest_email_id-1, -1):
#            typ, data = mail.fetch( i, '(RFC822)')
#        for response_part in data:
#            if isinstance(response_part, tuple):
#                msg = email.message_from_string(response_part[1])
#        varSubject = msg['subject']
#        varFrom = msg['from']
#        varFrom = varFrom.replace('<','')
#        varFrom = varFrom.replace('>','')

    #Remove used emails from mailbox
#    typ, data = mail.search(None, 'ALL')
#    for num in data[0].split():
#        mail.store(num, '+FLAGS', '\\Deleted')
#        mail.expunge()
#        mail.close()
#        mail.logout()
#
#   return int(varSubject)
#    return varSubject


####   if (read_gmail() > read_temp()):#Compare varSubject to temp

while True:
  read_gmail()
#  pprint.pprint(varSubject)
  wait(60)
  
