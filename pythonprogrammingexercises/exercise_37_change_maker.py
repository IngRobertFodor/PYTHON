# Change Maker

def change_maker(number):

    this_dict = {
        "quarters" : 0,
        "dimes" : 0,
        "nickels" : 0,
        "pennies" : 0
        }

    # Quarters
    quarters = number//25
    this_dict["quarters"] = quarters
    if this_dict["quarters"] == 0:
        this_dict.pop("quarters")
    q_change = number - (quarters*25)

    # Dimes
    dimes = q_change//10
    this_dict["dimes"] = dimes
    if this_dict["dimes"] == 0:
        this_dict.pop("dimes")
    d_change = q_change - (dimes*10)

    # Nickels
    if d_change>=5:
        nickels = d_change//5
        this_dict["nickels"] = nickels
        if this_dict["nickels"] == 0:
            this_dict.pop("nickels")
        n_change = d_change - (nickels*5)
        # Pennies
        pennies = n_change
        this_dict["pennies"] = pennies
        if this_dict["pennies"] == 0:
            this_dict.pop("pennies")
    else:
        nickels = 0
        this_dict["nickels"] = nickels
        if this_dict["nickels"] == 0:
            this_dict.pop("nickels")
        n_change = d_change - (nickels*5)
        # Pennies
        pennies = n_change
        this_dict["pennies"] = pennies
        if this_dict["pennies"] == 0:
            this_dict.pop("pennies")
    
    return this_dict


# Asserts
assert change_maker(30) == {'quarters': 1, 'nickels': 1} 
assert change_maker(10) == {'dimes': 1} 
assert change_maker(57) == {'quarters': 2, 'nickels': 1, 'pennies': 2} 
assert change_maker(100) == {'quarters': 4} 
assert change_maker(125) == {'quarters': 5}


result = change_maker(38)
print(result)