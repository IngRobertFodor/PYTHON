import random
import collections


def roll_dice(x, y, z):
    rx = random.randint(1, x)
    ry = random.randint(1, y)
    rz = random.randint(1, z)
    
    sum_rx_ry_rz = rx + ry + rz
    return sum_rx_ry_rz


my_list = []
dice_rolled_times = 1000000
for i in range(dice_rolled_times):
    my_list.append(roll_dice(4, 6, 6))
my_dict = dict(collections.Counter(my_list))
print(my_dict)

for key, occured in my_dict.items():
    perc = (occured / dice_rolled_times) * 100
    #print(perc)
    rounded_perc = round(perc, 2)
    #print(rounded_perc)
    print(f"{key} occured {rounded_perc} % of the time.")