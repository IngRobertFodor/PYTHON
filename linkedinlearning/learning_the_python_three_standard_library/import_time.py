import time
from datetime import datetime


time.sleep(4)
print("4 seconds have passed.")
print()

users_input = input("Enter a number of seconds from 0 to 5: ")
seconds = 1
while seconds < int(users_input)+1:
    print(seconds, "second")
    time.sleep(1)
    seconds += 1
print(str(users_input), "seconds have passed.")
print()

time_now = datetime.now().time()
print(time_now)
time.sleep(4)
time_after_few_seconds = datetime.now().time()
print(time_after_few_seconds)