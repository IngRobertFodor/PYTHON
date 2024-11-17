from datetime import datetime
from datetime import timedelta


date = datetime.now().date()
print(date)
time = datetime.now().time()
print(time)
now = datetime.now()
print(now)
print()

print(date.year)
print(date.month)
print(date.day)
print()

print(time.hour)
print(time.minute)
print(time.second)
print()

# %A is the full name of the day of the week
print(now.strftime("%A"))
print(now.strftime("%d:%m:%Y - %A"))
print()

in_five_days = now + timedelta(days=5)
print("In five days from now is: ", in_five_days)
print("In five days from now is: ", in_five_days.day)
print("In five days from now is: ", in_five_days.strftime("%A"))
five_weeks_ago = now - timedelta(weeks=5)
print("Five weeks ago was: ", five_weeks_ago)
print("Five weeks ago was: ", five_weeks_ago.date())
print("Five weeks ago was: ", five_weeks_ago.strftime("%A"))
print()