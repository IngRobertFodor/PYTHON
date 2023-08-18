# The Fourth best way for PC to guess.
# Using "Binary search".      
def play_game_four_binary_search(list_a, my_number, low=None, high=None, count=0):
    
    if low is None:
        low = 0
    if high is None:
        high = len(list_a) - 1
    if high < low:
        return False
    
    midpoint = (low + high) // 2
    # Our midpoint is 49, because "list_a[49] == 50".
    if list_a[midpoint] == my_number:
        count += 1
        return count
    
    elif my_number < list_a[midpoint]:
        new_high = midpoint - 1
        count += 1
        return play_game_four_binary_search(list_a, my_number, low, new_high, count)

    else:
        # elif my_number > list_a[midpoint]:
        new_low = midpoint + 1
        count += 1
        return play_game_four_binary_search(list_a, my_number, new_low, high, count)    


if __name__ == "__main__":
    # The Fourth best way for PC to guess.
    # Using "Binary search".
    
    # List of digits 1-100 (including 1 and 100).
    list_a = list(range(1,101))
    my_number = 88
    print("PC needed this many guesses.")
    print(play_game_four_binary_search(list_a, my_number))
