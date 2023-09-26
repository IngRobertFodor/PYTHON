#1 In how many assignment pairs does one range fully contain the other?

import string
import collections


with open("2022_04.txt", "r") as open_file:
    
    lines = open_file.readlines()
    print(lines)
    print(len(lines))
    
    list_items = []
    for i in range(0,len(lines)):
        item = lines[i].strip()
        list_items.append(item)
    print(list_items)

    split_list_items = []
    for i in range(0, len(list_items)):
        split = list_items[i].split(",")
        split_list_items.append(split)
    print(split_list_items)

    sub = []
    for i in range(0,len(split_list_items)):
        # print(split_list_items[i][0])
        a = split_list_items[i][0].split("-")[0]
        z = split_list_items[i][0].split("-")[1]
        a = int(a)
        z = int(z)
        print(a)
        print(z)
        range_a_z = list(range(a,z+1))
        print(range_a_z)
        # print(split_list_items[i][1])
        aa = split_list_items[i][1].split("-")[0]
        zz = split_list_items[i][1].split("-")[1]
        aa = int(aa)
        zz = int(zz)
        print(aa)
        print(zz)
        range_aa_zz = list(range(aa,zz+1))
        print(range_aa_zz)
        sub_one = set(range_a_z).issuperset(set(range_aa_zz))
        if sub_one == True:
            sub.append(sub_one)
        sub_two = set(range_aa_zz).issuperset(set(range_a_z))
        if sub_two == True:
            sub.append(sub_two)
        if range_a_z == range_aa_zz:
            sub.append("Adjust")        
        print(sub)

        print()
        print("Result is sum of counted 'True' values minus number of counted 'Adjust' values.")
        print(collections.Counter(sub))
        print("Result is 536.")