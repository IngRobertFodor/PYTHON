import random


# random.random()

# Returns a random float between 0 and 1.
print(random.random())
# Output: e.g 0.37444887175646646


# random.randint()

# Returns a random integer between the specified integers.
# Difference between randint() and randrange() is that randint() INCLUDES THE LAST NUMBER in the range.
print(random.randint(1, 100))
# Output: e.g 25


# random.randrange()

# Returns a random integer between the specified integers.
# Difference between randint() and randrange() is that randrange() DOES NOT INCLUDE THE LAST NUMBER in the range.
print(random.randrange(1, 100))
# Output: e.g 25


# random.sample()

print(random.sample([1, 2, 3, 4, 5], 3))
# Output: e.g [2, 4, 5]


# random.choices()

print(random.choices([1, 2, 3, 4, 5], k=3))
# Output: e.g [2, 4, 5]


# random.choice()

print(random.choice([1, 2, 3, 4, 5]))
# Output: e.g 5
print(random.choice(["apple", "banana", "cherry"]))
# Output: e.g banana


# random.shuffle()

x = [1, 2, 3, 4, 5]
random.shuffle(x)
print(x)
# Output: e.g [3, 2, 5, 1, 4]