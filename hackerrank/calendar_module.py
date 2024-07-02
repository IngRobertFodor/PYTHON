import calendar


week_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
specified_date = "08 05 2015"
month, day, year = map(int, specified_date.split())
print(day)
print(month)
print(year)
if year in range(2001, 3000):
    day_of_week_num = calendar.weekday(year, month, day)
    print(day_of_week_num)
    day_of_week = week_days[day_of_week_num]
    print(day_of_week.upper())