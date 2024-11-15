# round()

print(round(3.15159, 2))
# Output: 3.15


# pow()

print(pow(2, 3))
# Output: 8


# abs()

print(abs(-10))
# Output: 10


# sorted()

    # sort in ascending order and case sensitive is default
print(sorted([5, 2, 3, 1, 4]))
# Output: [1, 2, 3, 4, 5]
    # sort in ascending order and case sensitive is default
print(sorted(['cat', 'dog', 'elephant', 'bird']))
# Output: ['bird', 'cat', 'dog', 'elephant']
    # sort in ascending order and case sensitive is default
print(sorted(['cat', 'Dog', 'elephant', 'bird']))
# Output: ['Dog', 'bird', 'cat', 'elephant']

    # sort in descending order
print(sorted([5, 2, 3, 1, 4], reverse=True))
# Output: [5, 4, 3, 2, 1]

    # case insensitive sort
print(sorted(['cat', 'Dog', 'elephant', 'bird'], key=str.upper))
# Output: ['bird', 'cat', 'Dog', 'elephant']

    # sort by length of the string
print(sorted(['cat', 'Dog', 'elephant', 'bird'], key=len))
# Output: ['cat', 'Dog', 'bird', 'elephant']


leaderboard = {221: 'Chris', 163: 'Kev', 432: 'Samuel', 321: 'Tom'}
# sort by key
print(sorted(leaderboard, reverse=True))
# Output: [432, 321, 221, 163]
print(leaderboard.get(432))
# Output: Samuel


# min()
# max()
# len()
# sum()
# all()
# any()
# type()
# isinstance()