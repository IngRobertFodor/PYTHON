# Hours, Minutes, Seconds

def get_hours_minutes_seconds(original_seconds):
    
    if original_seconds == 0:
        result = "0s"
    
    raw_hours = original_seconds / 3600
    hours = int(raw_hours)
    days = ""
    if hours >= 24:
        days = hours // 24
        my_days = str(days) + "d"
        my_hours = hours % 24
        my_hours = str(my_hours) + "h"
    else:
        my_hours = str(hours) + "h"
    
    raw_minutes = (raw_hours - int(raw_hours)) * 60
    minutes = int(raw_minutes)
    my_minutes = str(minutes) + "m"
    
    raw_seconds = (raw_minutes - int(raw_minutes)) * 60
    seconds = round(raw_seconds)
    my_seconds = str(seconds) + "s"
    
    if (hours//24) < 1:
        result = my_hours + " " + my_minutes + " " + my_seconds
    else:
        result = my_days + " " + my_hours + " " + my_minutes + " " + my_seconds
    
    return print(result)


get_hours_minutes_seconds(0)
get_hours_minutes_seconds(30)
get_hours_minutes_seconds(60)
get_hours_minutes_seconds(90)
get_hours_minutes_seconds(3600)
get_hours_minutes_seconds(3601)
get_hours_minutes_seconds(3661)
get_hours_minutes_seconds(90042)
get_hours_minutes_seconds(12345678)