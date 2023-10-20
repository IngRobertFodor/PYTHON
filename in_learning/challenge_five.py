# Number 1 is not prime number.
# List all prime numbers to my_number.

def find_prime_numbers(my_number):
    prime_numbers_list_to_my_number = []
    for num in range(2,my_number):
        prime = True
        for i in range(2,num):
            if (num%i==0):
                prime = False
        if prime:
            #print(num)
            prime_numbers_list_to_my_number.append(num)

    return print(prime_numbers_list_to_my_number)

find_prime_numbers(20)
find_prime_numbers(150)