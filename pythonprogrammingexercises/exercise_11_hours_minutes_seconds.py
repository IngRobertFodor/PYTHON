# Hours, Minutes, Seconds

def get_hours_minutes_seconds(original_seconds):
       
    raw_hours = original_seconds / 3600
    hours = int(raw_hours)
    result = []
    my_days = ""
    my_hours = ""
    my_minutes = ""
    my_seconds = ""
    if hours >= 24:
        days = hours // 24
        my_days = str(days) + "d"
        result.append(my_days)
        my_hours = hours % 24
        if my_hours > 0:
            my_hours = str(my_hours) + "h"
            result.append(my_hours)
    else:
        if hours > 0:
            my_hours = str(hours) + "h"
            result.append(my_hours)
    
    raw_minutes = (raw_hours - int(raw_hours)) * 60
    minutes = int(raw_minutes)
    if minutes > 0:
        my_minutes = str(minutes) + "m"
        result.append(my_minutes)
    
    raw_seconds = (raw_minutes - int(raw_minutes)) * 60
    seconds = round(raw_seconds)
     
    if original_seconds == 0:
        result = ['0s']
    elif seconds > 0:
        my_seconds = str(seconds) + "s"
        result.append(my_seconds)
    
    return result


result_one = get_hours_minutes_seconds(0)
print(result_one)
result_two = get_hours_minutes_seconds(30)
print(result_two)
result_three = get_hours_minutes_seconds(60)
print(result_three)
result_four = get_hours_minutes_seconds(90)
print(result_four)
result_five = get_hours_minutes_seconds(3600)
print(result_five)
result_six = get_hours_minutes_seconds(3601)
print(result_six)
result_seven = get_hours_minutes_seconds(3661)
print(result_seven)
result_eight = get_hours_minutes_seconds(90042)
print(result_eight)
result_nine = get_hours_minutes_seconds(12345678)
print(result_nine)