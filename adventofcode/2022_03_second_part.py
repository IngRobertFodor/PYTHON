with open("2022_03.txt", "r") as open_file:
    
    lines = open_file.readlines()
    print(lines)
    print(len(lines))
    
    list_items = []
    for i in range(0,len(lines)):
        item = lines[i].strip()
        list_items.append(item)
    print(list_items)

    list_items_splitted = []
    chunk_size = 3
    for i in range(0, len(list_items), chunk_size):
        list_items_splitted.append(list_items[i:i+chunk_size])
    print(list_items_splitted)