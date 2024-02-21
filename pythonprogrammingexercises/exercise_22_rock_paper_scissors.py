# Rock, Paper, Scissors

def rock_paper_scisssors(player_one,player_two):
    
    game_moves = ("rock", "paper", "scissors")

    if player_one == player_two:
        return "Tie"
    elif player_one != player_two:
        if player_one == game_moves[0] and player_two == game_moves[2]:
            return "Player One"
        elif player_one == game_moves[1] and player_two == game_moves[0]:
            return "Player One"
        elif player_one == game_moves[2] and player_two == game_moves[1]:
            return "Player One"
        else:
            return "Player Two"


# Asserts
assert rock_paper_scisssors("rock", "paper") == "Player Two" 
assert rock_paper_scisssors("rock", "scissors") == "Player One" 
assert rock_paper_scisssors("paper", "scissors") == "Player Two" 
assert rock_paper_scisssors("paper", "rock") == "Player One" 
assert rock_paper_scisssors("scissors", "rock") == "Player Two" 
assert rock_paper_scisssors("scissors", "paper") == "Player One" 
assert rock_paper_scisssors("rock", "rock") == "Tie" 
assert rock_paper_scisssors("paper", "paper") == "Tie" 
assert rock_paper_scisssors("scissors", "scissors") == "Tie"


result_one = rock_paper_scisssors("paper", "rock")
print(result_one)
result_two = rock_paper_scisssors("paper", "paper")
print(result_two)
result_three = rock_paper_scisssors("rock", "paper")
print(result_three)