import random


def generate_special_password(num):

    dice_num_list = []
    for i in range(num):
        i = random.randint(1, 7)
        dice_num_list.append(str(i))
    print(dice_num_list)
    dice_num = "".join(dice_num_list)
    print(dice_num)

    password_file = open("dicewarewordlist.pdf", "r")
    
    return


generate_special_password(5)