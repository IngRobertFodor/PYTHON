import random


def generate_special_password(number_representing_length_of_password):

    dice_num_list = []
    generated_password = []
    for i in range(number_representing_length_of_password):
        for j in range(5):
            j = random.randrange(1, 7)
            dice_num_list.append(str(j))
        print(dice_num_list)
        dice_num = "".join(dice_num_list)
        print(dice_num)
        dice_num_list.clear()
        
        password_file = open("dicewarewordlist.txt", "r")
        for line in password_file:
            #print(line)
            line_list = list(line.split())
            #print(line_list)
            if len(line_list)==2 and dice_num == line_list[0]:
                print(line_list[1])
                generated_password.append(line_list[1])
                break
    print(generated_password)
    generated_password = " ".join(generated_password)
    print()

    password_file.close()
    
    return print("Password generated successfully:", generated_password)


generate_special_password(5)