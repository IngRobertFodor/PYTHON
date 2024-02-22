# Every 15 Minutes

am_pm = ("am","pm")
hours = ("12", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11")
minutes = ("00", "15", "30", "45")

for am_vs_pm in range(2): 
    for hour in range(12):
        for each_fifteen_minutes in range(4):
            x = hours[hour],minutes[each_fifteen_minutes]
            #print(x)
            xx = ":".join(x)
            #print(xx)
            xxx = xx, am_pm[am_vs_pm]
            #print(xxx)
            xxxx = " ".join(xxx)
            print(xxxx)