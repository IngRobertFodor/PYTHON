import time
import random


#referenced_time = 4.0
referenced_time = random.randrange(2,9)
print("Your reference time is", referenced_time, "seconds.")

input("Press Enter to start the timer")
start_time = time.time()
input("Press Enter to stop the timer")
elapsed_time = time.time() - start_time
formated_elapsed_time = "{:.0f}".format(elapsed_time)
print("Elapsed time: ", formated_elapsed_time, "seconds")

formated_elapsed_time = float(formated_elapsed_time)

if formated_elapsed_time < referenced_time:
    print("You're too impatient.")
elif formated_elapsed_time > referenced_time:
    print("You're too patient.")
else:
    # formated_elapsed_time == referenced_time
    print("You're right on time.")