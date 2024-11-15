import itertools


# itertools.count(start, step)

for c in itertools.count(50, 5):
    print(c)
    if c == 60:
        break
print()


# itertools.cycle(iterable)

x = 0
for c in itertools.cycle([1, 2, 3, 4]):
    print(c)
    x = x + 1
    if x > 10:
        break

x = 0
for c in itertools.cycle("Cycle"):
    print(c)
    x = x + 1
    if x > 10:
        break
print()


# itertools.repeat(object)

x = 0
for r in itertools.repeat(True):
    print(r)
    x = x + 1
    if x > 5:
        break

x = 0
for r in itertools.repeat("Repeat"):
    print(r)
    x = x + 1
    if x > 5:
        break
print()


# itertools.permutations()

# Permutations are all possible orderings of a collection of items.
# Dupicate items are allowed.
letters = ['a', 'b', 'c', 'd']
result = itertools.permutations(letters, 2)
for item in result:
    print(item)
# ('a', 'b')
# ('a', 'c')
# ('a', 'd')
# ('b', 'a')
# ('b', 'c')
# ('b', 'd')
# ('c', 'a')
# ('c', 'b')
# ('c', 'd')
# ('d', 'a')
# ('d', 'b')
# ('d', 'c') 
print()


# itertools.combinations()

# Combinations are all possible selections of a collection of items.
# Duplicate items are skipped.
letters = ['a', 'b', 'c', 'd']
result = itertools.combinations(letters, 2)
for item in result:
    print(item)
# ('a', 'b')
# ('a', 'c')
# ('a', 'd')
# ('b', 'c')
# ('b', 'd')
# ('c', 'd')