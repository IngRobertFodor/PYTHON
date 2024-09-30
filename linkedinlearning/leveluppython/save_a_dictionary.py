import json


def save_my_dict_to_file(my_dict):
    dict_file_name = str(input("Enter the file name: "))
    dict_file = open(dict_file_name, "w")
    
    # Write the dictionary to the file.
    json.dump(my_dict, dict_file)

    dict_file.close()
    return dict_file_name


def open_and_read_new_file(dict_file_name):
    file_to_read = open(dict_file_name, "r")
    return file_to_read.read()


my_test_dict = {"name": "John", "age": 30, "city": "New York"}


retrieved_dict = open_and_read_new_file(save_my_dict_to_file(my_test_dict))
print(retrieved_dict)