import time
import calendar

#import thermoschedule
# schedulazione della programmazione della temperatura
#mySchedule is a matrix [7 x 24] [lunedi' is first row]
mySchedule = [['17' for x in range(7)] for x in range(24)] 

try:
   fileschedule = open("fileschedule","r")  #apre il file dei dati in append mode, se il file non esiste lo crea
   for i in range (0,7):
   #for y in range (0,25):
        tmpstr=fileschedule.readline().strip(",\n")
        print "tmpstr["+str(i)+"]="+tmpstr
        mySchedule[i]=tmpstr.split(",")  #scrive la info di presence ed il timestam sul file
   fileschedule.close()  #chiude il file dei dati e lo salva
except IOError:
   mySchedule= [['17','17','17','17','17','17','20','20','20','18','18','18','18','20','20','18','18','18','18','18','20','20','20','17'],
                ['17','17','17','17','17','17','20','20','20','18','18','18','18','20','20','18','18','18','18','18','20','20','20','17'],
                ['17','17','17','17','17','17','20','20','20','18','18','18','18','20','20','18','18','18','18','18','20','20','20','17'],
                ['17','17','17','17','17','17','20','20','20','18','18','18','18','20','20','18','18','18','18','18','20','20','20','17'],
                ['17','17','17','17','17','17','20','20','20','18','18','18','18','20','20','18','18','18','18','18','20','20','20','17'],
                ['17','17','17','17','17','17','20','20','20','18','18','18','18','20','20','18','18','18','18','18','20','20','20','17'],
                ['17','17','17','17','17','17','17','17','20','20','18','18','18','20','20','20','18','18','18','18','20','20','20','17'],
                ['17','17','17','17','17','17','17','17','20','20','18','18','18','20','20','20','18','18','18','18','20','20','20','17']]

print mySchedule
print mySchedule[0][0]
print mySchedule[6][0]
print mySchedule[6][23]

#orario = time.localtime(time.time())
now = time.time()
orario = time.localtime(now)
   

curr_year=int(time.strftime("%Y",orario))
curr_month=int(time.strftime("%m",orario)) 
curr_day=int(time.strftime("%e",orario))
curr_hour=int(time.strftime("%H",orario))

localtime = time.asctime( orario )
day_of_week= calendar.weekday(curr_year,curr_month,curr_day)

print "localtime:",localtime, " day_of_week:", day_of_week, " curr_hour:",curr_hour," temp target:", mySchedule[day_of_week][curr_hour] 
print mySchedule
print mySchedule[0][0]
print mySchedule[6][0]
print mySchedule[6][23]


fileschedule = open("fileschedule","w")  #apre il file dei dati in append mode, se il file non esiste lo crea
for i in range (0,7):
   for y in range (0,24):
      fileschedule.write(str(mySchedule[i][y])+",")
      fileschedule.write("\n")#scrive la info di presence ed il timestam sul file
fileschedule.close()  #chiude il file dei dati e lo salva

#fileschedule = open("fileschedule","rb")  #apre il file dei dati in append mode, se il file non esiste lo crea
#fileschedule.read(mySchedule)  #scrive la info di presence ed il timestam sul file
#fileschedule.close()  #chiude il file dei dati e lo salva

print mySchedule
print mySchedule[0][0]
print mySchedule[6][0]
print mySchedule[6][23]
