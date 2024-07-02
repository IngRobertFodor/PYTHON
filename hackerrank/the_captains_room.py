from collections import Counter


k = 5
#my_data = map(int, input().split())
my_data = [1, 2, 3, 5, 3, 5, 3, 8, 1, 2, 3, 5, 3, 5, 3,1, 2, 3, 5, 3, 5, 3]
if k in range(0, 1000):
    my_dict = Counter(my_data) 
    for item, count in my_dict.items():
        if count == 1:
            print(item)