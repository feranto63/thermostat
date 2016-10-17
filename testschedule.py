import time
import calendar

dbname='/var/www/templog.db'

# schedulazione della programmazione della temperatura
#mySchedule is a matrix [7 x 24] [lunedi' is first row]
mySchedule = [['17' for x in range(24)] for x in range(7)] 
print mySchedule

import sqlite3

# store the temperature in the database
def get_termoschedule():

   conn=sqlite3.connect(dbname)
   curs=conn.cursor()
   curs.execute("SELECT * FROM termoschedule")
   for i in range (0,7):
      mySchedule[i]=curs.fetchone()
      print (mySchedule[i])
      print"\n"
         
   conn.close()


get_thermoschedule()
