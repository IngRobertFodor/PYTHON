from itertools import combinations


# Handshakes

my_list = ['Alice', 'Bob', 'Carol', 'David']

def handshakes(names):
    res = list(combinations(names, 2))
    #print(res)
    return len(res)


# Asserts
assert handshakes(['Alice', 'Bob']) == 1 
assert handshakes(['Alice', 'Bob', 'Carol']) == 3 
assert handshakes(['Alice', 'Bob', 'Carol', 'David']) == 6   


print(handshakes(my_list))