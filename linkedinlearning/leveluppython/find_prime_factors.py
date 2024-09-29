# pip install sympy
import sympy # type: ignore


# These are the prime numbers between 1 and 100.
primes = list(sympy.primerange(1, 101))
#for prime in primes:
#    print(prime)

# This is the number we want to find the prime factors for.
num = 630

res = []
prime_res = []
divisor = 2
while num > 1:
    while num % divisor == 0:
        res.append(divisor)
        num //= divisor
    else:
        divisor += 1

#print(res)
for i in res:
    if i in primes:
        prime_res.append(i)
print(prime_res)