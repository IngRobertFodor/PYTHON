import string


with open("2022_03.txt", "r") as open_file:
    
    lines = open_file.readlines()
    print(lines)
    print(len(lines))
    
    list_items = []
    for i in range(0,len(lines)):
        item = lines[i].strip()
        list_items.append(item)
    print(list_items)

    elf_items = []
    for item in list_items:
        n = len(item)
        print(n)
        if n%2 == 0:
            string_one = set(item[0:n//2])
            string_two = set(item[n//2:])
            print("First Half of String:",string_one)
            print("Second Half of String:",string_two)
            unique = set(string_one).intersection(set(string_two))
            print(f" This is item from backpack that is unique: {unique}.")
            elf_items.append(unique)
        else:
            string_one = set(item[0:(n//2+1)])
            string_one = set(item[(n//2+1):])
            print("First Half of String:",string_one)
            print("Second Half of String:",string_two)
            unique = set(string_one).intersection(set(string_two))
            print(f" This is item from backpack that is unique: {unique}.")
            elf_items.append(unique)
    print(elf_items)

    elf_items_strings_first = []
    for i in elf_items:
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
    elf_items_strings_second
    elf_items_strings = elf_items_strings_second
    print(elf_items_strings)

    elf_items_strings_lower_case = []
    elf_items_strings_upper_case = []
    for i in elf_items_strings:
        if i in string.ascii_lowercase:
            elf_items_strings_lower_case.append(i)
        else:
            elf_items_strings_upper_case.append(i)
    print()
    print(elf_items_strings_lower_case)
    print(elf_items_strings_upper_case)

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
    print(xx)
    print(f"This is sum of priority values in backpack: {sum(xx)}.")
