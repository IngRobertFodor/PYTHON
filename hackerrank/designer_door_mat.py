n = 7
m = 3*n
#print("N: ", n)
#print("M: ", m)
my_string = "WELCOME"

countve = -1

if n in range(6, 101):
    
    for row in range(1, (n//2)+1):     
        countve += 2
        countho = m-(3*countve)
        #print("COUNTVE: ", countve)
        #print("COUNTHO: ", countho)
        print("-" * (countho//2), end="")
        print(".|." * countve, end="")
        print("-" * (countho//2), end="")
        print()
    
    #print("WELCOME".center(m, "-"))
    countwe = (m-len(my_string))//2
    #print("COUNTWE: ", countwe)
    print("-" * countwe, end="")
    print("WELCOME", end="")
    print("-" * countwe, end="")
    print()

    for row in range((n//2), 0, -1):     
        countho = m-(3*countve)
        #print("COUNTVE: ", countve)
        #print("COUNTHO: ", countho)
        print("-" * (countho//2), end="")
        print(".|." * countve, end="")
        print("-" * (countho//2), end="")
        print()
        countve -= 2