import time

import thermoschedule.py

orario = time.localtime(now)
curr_year=num(strftime("%Y",orario))
curr_month=num(strftime("%m",orario)) 
curr_day=num(strftime("%e",orario))
curr_hour=num(strftime("%H",orario))
localtime = time.asctime( orario )
day_of_week= calendar.weekday(curr_year,curr_month,curr_day)

print "localtime:",localtime, " day_of_week:", day_of_week, " curr_hour:",curr_hour," temp target:", mySchedule[day_of_week,curr_hour+1] 
