import re


### re.split()

# \W+ means any non-word character
# note: \W is a non-word character, + is one or more
my_string = 'A! B. C D'
pattern = r'\W+'
res = re.split(pattern, my_string)
# Output: ['A', 'B', 'C', 'D']
print(res)

# how to return string: "ABCD"?
# use join() method
# Output: ABCD
print(''.join(res))
print()


### re.findall()

# find all the words that start with 'bl'
my_string = "blick, blue and brown, blond"
pattern = r'bl\w+'
matches = re.findall(pattern, my_string)
print(matches)