def sort_string(text):
    
    print(text)

    # Sort the list, but capitalized strings go first.
    text_list = list(text.split())
    text_list.sort()
    print(text_list)
    # Sort the list, but do not consider the case.
    text_list.sort(key=str.lower)
    print(text_list)
    print()
    return " ".join(text_list)


print("This is my answer: ", sort_string("See a A SORTED string FOR ME"))
print()
print("This is my answer: ", sort_string("banana ORANGE apple"))