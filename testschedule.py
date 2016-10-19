import time
import calendar

dbname='/var/www/templog.db'

week_name=['DOM','LUN','MAR','MER','GIO','VEN','SAB'] #domenica = 0

today = 2

# schedulazione della programmazione della temperatura
#mySchedule is a matrix [7 x 24] [lunedi' is first row]
mySchedule = [['17' for x in range(24)] for x in range(7)] 
print (mySchedule)

import sqlite3

# read the comfort temperature table fron database
def get_tempschedule():
   global mySchedule, week_name, dbname
   conn=sqlite3.connect(dbname)
   curs=conn.cursor()
   curs.execute("SELECT * FROM tempschedule")
   for i in range (7):
      data=curs.fetchone()
      day_index=week_name.index(data[0])
      print (data)
      for j in range (24):
         mySchedule[day_index][j]=data[j+1]
         print (mySchedule[day_index][j])
         print("-")
      print("\n")
         
   conn.close()

def put_tempschedule(day,time,temp):
   day_index = week_name[day]
   if time < 10:
      column_name = "h0"+str(time)
   else:
      column_name = "h"+str(time)
   
   conn=sqlite3.connect(dbname)
   curs=conn.cursor()
   command="UPDATE tempschedule SET "+column_name+" = ? WHERE giorno = ?"
#   command="UPDATE tempschedule SET h17 = ? WHERE giorno = ?"
   curs.execute(command, (temp, day_index)) 
#   curs.execute("SELECT * FROM tempschedule")
#   for i in range (7):
#      data=curs.fetchone()
#      print (data)
#      for j in range (24):
#         mySchedule[i][j]=data[j+1]
#         print (mySchedule[i][j])
#         print("-")
#      print("\n")
         
   conn.close()
   
get_tempschedule()

while 1:
   day = int(input ("giorno :"))
   hour= int(input ("ora    :"))
   temp= float(input ("temp   :"))
   mySchedule[day][hour] = temp
   put_tempschedule(day,hour,temp)
   print (mySchedule)

