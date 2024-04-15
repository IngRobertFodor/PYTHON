# Colatz Sequence

def collatz_sequence(n):
    
    my_collatz_sequence_list = []
    
    if isinstance(n,int)==False or n<1:
        return my_collatz_sequence_list
    
    elif isinstance(n,int)==True and n>=1:
        my_collatz_sequence_list.append(n)
        while True:
            if n%2==0 and n!=1:
                n=n//2
                my_collatz_sequence_list.append(n)
            elif n%2!=0 and n!=1:
                n=3*n+1
                my_collatz_sequence_list.append(n)
            else:
                # isinstance(n,int)==True and n==1:
                return my_collatz_sequence_list


# Asserts
assert collatz_sequence(0) == [] 
assert collatz_sequence(10) == [10, 5, 16, 8, 4, 2, 1] 
assert collatz_sequence(11) == [11, 34, 17, 52, 26, 13, 40, 20, 10, 5, 16, 8, 4, 2, 1] 
assert collatz_sequence(12) == [12, 6, 3, 10, 5, 16, 8, 4, 2, 1] 
assert len(collatz_sequence(256)) == 9 
assert len(collatz_sequence(257)) == 123 
import random 
random.seed(42) 
for i in range(1000): 
    startingNum = random.randint(1, 10000) 
    seq = collatz_sequence(startingNum) 
    assert seq[0] == startingNum # Make sure it includes the starting number. 
    assert seq[-1] == 1  # Make sure the last integer is 1.


print(collatz_sequence(10))