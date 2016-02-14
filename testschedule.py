import time
import calendar

#import thermoschedule
# schedulazione della programmazione della temperatura
#mySchedule is a matrix [7 x 25]
mySchedule=[["lun",17,17,17,17,17,17,20,20,20,18,18,18,18,20,20,18,18,18,18,18,20,20,20,17],
            ["mar",17,17,17,17,17,17,20,20,20,18,18,18,18,20,20,18,18,18,18,18,20,20,20,17],
            ["mer",17,17,17,17,17,17,20,20,20,18,18,18,18,20,20,18,18,18,18,18,20,20,20,17],
            ["gio",17,17,17,17,17,17,20,20,20,18,18,18,18,20,20,18,18,18,18,18,20,20,20,17],
            ["ven",17,17,17,17,17,17,20,20,20,18,18,18,18,20,20,18,18,18,18,18,20,20,20,17],
            ["sab",17,17,17,17,17,17,17,17,20,20,18,18,18,20,20,20,18,18,18,18,20,20,20,17],
            ["dom",17,17,17,17,17,17,17,17,20,20,18,18,18,20,20,20,18,18,18,18,20,20,20,17]]
 
 
#orario = time.localtime(time.time())
now = time.time()
orario = time.localtime(now)
   

curr_year=int(time.strftime("%Y",orario))
curr_month=int(time.strftime("%m",orario)) 
curr_day=int(time.strftime("%e",orario))
curr_hour=int(time.strftime("%H",orario))

localtime = time.asctime( orario )
day_of_week= calendar.weekday(curr_year,curr_month,curr_day)

print "localtime:",localtime, " day_of_week:", day_of_week, " curr_hour:",curr_hour," temp target:", mySchedule[day_of_week][curr_hour+1] 
print mySchedule
print mySchedule[0][0]
print mySchedule[6][0]
print mySchedule[6][24]


fileschedule = open("fileschedule","w")  #apre il file dei dati in append mode, se il file non esiste lo crea
for i in range (0,7):
            for y in range (0,25):
                        fileschedule.write(str(mySchedule[i][y])+"\n")  #scrive la info di presence ed il timestam sul file
fileschedule.close()  #chiude il file dei dati e lo salva

#fileschedule = open("fileschedule","rb")  #apre il file dei dati in append mode, se il file non esiste lo crea
#fileschedule.read(mySchedule)  #scrive la info di presence ed il timestam sul file
#fileschedule.close()  #chiude il file dei dati e lo salva
fileschedule = open("fileschedule","r")  #apre il file dei dati in append mode, se il file non esiste lo crea
for i in range (0,7):
            for y in range (0,25):
                        mySchedule[i][y]=fileschedule.read().splitlines()  #scrive la info di presence ed il timestam sul file
fileschedule.close()  #chiude il file dei dati e lo salva

print mySchedule
