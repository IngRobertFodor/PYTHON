# !!! RUN THIS FIRST (CMD)
# pip install sympy
import sympy # type: ignore


# These are the prime numbers between 1 and 100.
primes = list(sympy.primerange(1, 101))
#for prime in primes:
#    print(prime)


def prime_factors(num):

    res = []
    prime_res = []

    divisor = 2

    while num > 1:
        if num % divisor == 0:
            res.append(divisor)
            num //= divisor
        else:
            divisor += 1

    for i in res:
        if i in primes:
            prime_res.append(i)
    return prime_res


print(prime_factors(630))
print(prime_factors(15))