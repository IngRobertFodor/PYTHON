file_path = "groceries.txt"
with open(file_path, "r") as file:
    data = file.read()
    print("data:", data)
    parsed_data = data.split(", ")
    print("parsed data:", parsed_data)
    print("item at index 2:", parsed_data[2])
    file.close()

my_file = open("groceries.txt", "r")
data = my_file.read()
print("data:", data)
parsed_data = data.split(", ")
print("parsed data:", parsed_data)
print("item at index 2:", parsed_data[2])
my_file.close()