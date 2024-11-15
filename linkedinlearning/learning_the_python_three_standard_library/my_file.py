'''
with open("my_file.txt", "r+") as f:
    print(f.read())
'''

# Read and write to a file.
my_file = open("my_file.txt", "w")
my_file.write("Hello, World!")
my_file.close()

my_file = open("my_file.txt", "r")
print(my_file.read())
my_file.close()