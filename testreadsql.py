import sqlite3
import threading
import os
import glob
import time

#Sqlite Database where to store readings
dbname='/var/www/templog.db'

conn=sqlite3.connect(dbname)

selectQuery = "SELECT  * FROM  sqlite_sequence WHERE name = 'temps'"
cursor = conn.cursor()
cursor.moveToLast()
#curs=conn.cursor()
#dati_da_inserire = [orario,temp,tempDHT,humidity]
#curs.execute("INSERT INTO temps values (?,?,?,?)", dati_da_inserire)
rows = cursor.fetchone()
# commit the changes
conn.commit()
conn.close()

print rows
