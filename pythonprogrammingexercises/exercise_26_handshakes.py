# Handshakes

my_list = ['Alice', 'Bob', 'Carol', 'David']

def handshakes(names):
    counter = 0
    for i in range(0,len(names)):
        for j in range(i+1,len(names)):
            counter += 1
            print(names[i], "shakes hands with", names[j])
    return counter


# Asserts
assert handshakes(['Alice', 'Bob']) == 1 
assert handshakes(['Alice', 'Bob', 'Carol']) == 3 
assert handshakes(['Alice', 'Bob', 'Carol', 'David']) == 6   


print()
printed_counter = handshakes(my_list)
print(printed_counter)