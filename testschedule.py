import time

import thermoschedule

orario = time.localtime(time.time())
curr_year=int(strftime("%Y",orario))
curr_month=int(strftime("%m",orario)) 
curr_day=int(strftime("%e",orario))
curr_hour=int(strftime("%H",orario))
localtime = time.asctime( orario )
day_of_week= calendar.weekday(curr_year,curr_month,curr_day)

print "localtime:",localtime, " day_of_week:", day_of_week, " curr_hour:",curr_hour," temp target:", mySchedule[day_of_week,curr_hour+1] 
