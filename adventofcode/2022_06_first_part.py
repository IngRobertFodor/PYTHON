#1 How many characters need to be processed before the first start-of-packet marker is detected?


with open("2022_06.txt", "r") as open_file:
    
    text = open_file.read()
    print(text)

    text_list = []
    for i in text:
        text_list.append(i)
    print(text_list)

    chunksize = 4
    list_characters = [text_list[i: i + chunksize] for i in range(len(text_list) + 1 - chunksize)]
    print(list_characters)

    my_string_in_list = []
    for i in list_characters:
        if len(set(i)) == 4:
            my_string_in_list.append(i)
            break
    print(my_string_in_list) 

    my_string_converted_to_string = " ".join(my_string_in_list[0])
    my_string_converted_to_string = my_string_converted_to_string.replace(" ","")
    print(f'This is my string: {my_string_converted_to_string}.')
    
    my_string_position = text.find(str(my_string_converted_to_string))
    print(f'This is position of my string: {my_string_position}.')

    number_to_find_is = my_string_position+4
    print(f'This is number to find: {number_to_find_is}.')