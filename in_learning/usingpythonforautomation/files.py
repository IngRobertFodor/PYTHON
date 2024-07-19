# READ FILE
input_file = open("files_my_file.txt", "r")
for line in input_file:
    line_split = line.split()
    if line_split[2] == "P":
        print(line)
input_file.close()


# WRITE FILE
# Open input_file.txt with the intention of reading it.
input_file = open("files_my_file.txt", "r")
# Open pass_file.txt with the intention of writing it.
pass_file = open("pass_file.txt", "w")
# Open fail_file.txt with the intention of writing it.
fail_file = open("fail_file.txt", "w")

for line in input_file:
    line_split = line.split()
    if line_split[2] == "P":
        pass_file.write(line)
    else:
        fail_file.write(line)

# Close input_file.txt
input_file.close()

# Close pass_file.txt
pass_file.close()

# Close fail_file.txt
fail_file.close()