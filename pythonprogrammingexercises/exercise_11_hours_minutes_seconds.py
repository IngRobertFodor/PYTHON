# Hours, Minutes, Seconds

def get_hours_minutes_seconds(original_seconds):
    raw_hours = original_seconds / 3600
    #print(raw_hours)
    #print("Whole Hours:", int(raw_hours))
    hours = int(raw_hours)
    my_hours = str(hours) + "h"
    #print(my_hours)

    raw_minutes = (raw_hours - int(raw_hours)) * 60
    #print(raw_minutes)
    #print("Whole Minutes", int(raw_minutes))
    minutes = int(raw_minutes)
    my_minutes = str(minutes) + "m"
    #print(my_minutes)

    raw_seconds = (raw_minutes - int(raw_minutes)) * 60
    #print(raw_seconds)
    #print("Whole Seconds", int(raw_seconds))
    seconds = round(raw_seconds)
    my_seconds = str(seconds) + "s"
    #print(my_seconds)

    result = my_hours + " " + my_minutes + " " + my_seconds

    if original_seconds == 0:
        result = "0s"

    return print(result)


get_hours_minutes_seconds(0)
get_hours_minutes_seconds(30)
get_hours_minutes_seconds(60)
get_hours_minutes_seconds(90)
get_hours_minutes_seconds(3600)
get_hours_minutes_seconds(3601)
get_hours_minutes_seconds(3661)
get_hours_minutes_seconds(90042)