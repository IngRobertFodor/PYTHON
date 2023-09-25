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

    letters = []
    for i in list_items_splitted:
        x = set(i[0])&set(i[1])&set(i[2])
        letters.append(x)
    print(letters)

    elf_items_strings_first = []
    for i in letters:
        i = str(i)
        string_i = i.replace("{'", "")
        elf_items_strings_first.append(string_i)
    print(elf_items_strings_first)
    elf_items_strings_second = []
    for i in elf_items_strings_first:
        i = str(i)
        string_i = i.replace("'}", "")
        elf_items_strings_second.append(string_i)
    print(elf_items_strings_second)
    elf_items_strings = elf_items_strings_second
    print()
    print(elf_items_strings)

    # 52 numbers and 52 letters
    numbers = list(range(1,53))
    letters = ["a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z","A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z"]
    priority_values = dict(zip(letters, numbers))
    print(priority_values)
    k = list(priority_values.keys())
    v = list(priority_values.values())
    print(k)
    print(v)

    xx = []
    for i in elf_items_strings:
        if i in priority_values.keys():
            x = priority_values.get(i)
            xx.append(x)
    print()        
    print(xx)
    print(f"This is sum of priority values in backpack: {sum(xx)}.")