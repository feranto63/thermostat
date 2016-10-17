import time
import calendar

dbname='/var/www/templog.db'

# schedulazione della programmazione della temperatura
#mySchedule is a matrix [7 x 24] [lunedi' is first row]
mySchedule = [['17' for x in range(24)] for x in range(7)] 
print (mySchedule)

import sqlite3

# store the temperature in the database
def get_tempschedule():
   conn=sqlite3.connect(dbname)
   curs=conn.cursor()
   curs.execute("SELECT * FROM tempschedule")
   for i in range (7):
      data=curs.fetchone()
      print (data)
      for j in range (24):
         mySchedule[i][j]=data[j+1]
         print (mySchedule[i][j])
         print("-")
      print("\n")
         
   conn.close()

get_tempschedule()

while 1:
   day = int(input ("giorno :"))
   hour= int(input ("ora    :"))
   temp= float(input ("temp   :"))
   mySchedule[hour][day] = temp
   print (mySchedule)

