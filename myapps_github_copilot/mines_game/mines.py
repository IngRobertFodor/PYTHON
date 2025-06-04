# 💣Mine-Finding Game💣


import pygame #type: ignore
import random


# Initialize pygame
pygame.init()

# Constants
SIZE = 10    # Size of the board (10x10)
SQUARE_SIZE = 50    # Size of each square in pixels
BOARD_SIZE = SIZE * SQUARE_SIZE    # Total size of the board in pixels
INFO_PANEL_WIDTH = 280    # Width of the info panel
WINDOW_WIDTH = BOARD_SIZE + INFO_PANEL_WIDTH    # Total width of the window
LIGHT_BLUE = (173, 216, 230)    # Background color for the board
PALE_YELLOW = (255, 255, 102)    # Player 1
LIGHT_PURPLE = (180, 160, 255)    # Player 2
LIGHT_GREY = (211, 211, 211)    # Grid lines color
BLACK = (0, 0, 0)    # Text color
NATURAL_GREEN = (144, 238, 144)    # Info panel
SOFT_RED = (255, 105, 97)    # Summary
BUTTON_WIDTH, BUTTON_HEIGHT = 120, 50    # Dimensions for buttons

# Initialize the game window
win = pygame.display.set_mode((WINDOW_WIDTH, BOARD_SIZE))
pygame.display.set_caption("💣Mine-Finding Game💣")

# Load images
treasure_chest_img = pygame.image.load('treasure_chest.png')
mine_img = pygame.image.load('mine.png')

# Resize images to fit within a cell
treasure_chest_img = pygame.transform.scale(treasure_chest_img, (SQUARE_SIZE, SQUARE_SIZE))
mine_img = pygame.transform.scale(mine_img, (SQUARE_SIZE, SQUARE_SIZE))

# Fonts
font = pygame.font.SysFont(None, 50)    # Main font for game text

# Function to initialize the game state
def init_game():
    return {
        'mine_location': (random.randint(0, SIZE-1), random.randint(0, SIZE-1)),
        'board': [['-' for i in range(SIZE)] for i in range(SIZE)],
        'current_player': 1,
        'score1': SIZE * SIZE,
        'score2': SIZE * SIZE,
        'game_over': False,
        'last_click': None    # To store the last clicked cell
    }

game_state = init_game()

# Function to draw the game board
def draw_board():
    win.fill(LIGHT_BLUE)
    for row in range(SIZE):
        for col in range(SIZE):
            x, y = col * SQUARE_SIZE, row * SQUARE_SIZE
            if game_state['board'][row][col] == '-':
                pygame.draw.rect(win, LIGHT_BLUE, (x, y, SQUARE_SIZE, SQUARE_SIZE))
            elif game_state['game_over'] and (row, col) == game_state['last_click']:
                # Show the mine image at the last clicked location
                win.blit(mine_img, (x, y))
            else:
                win.blit(treasure_chest_img, (x, y))

            # Draw grid lines
            pygame.draw.rect(win, LIGHT_GREY, (x, y, SQUARE_SIZE, SQUARE_SIZE), 1)

    draw_info_panel()
    pygame.display.update()

def draw_info_panel():
    # Draw the info panel background
    panel_x = BOARD_SIZE
    pygame.draw.rect(win, NATURAL_GREEN, (BOARD_SIZE, 0, INFO_PANEL_WIDTH, BOARD_SIZE))
    
    # Use a smaller font for better spacing for the info panel
    small_font = pygame.font.SysFont(None, 20)    # Decreased font size to 20

    # Display current player's turn
    text = small_font.render(f"Player {game_state['current_player']}'s Turn", True, BLACK)
    win.blit(text, (panel_x + 10, 10))

    # Display scores (Player 1 first, Player 2 second)
    score_text1 = small_font.render(f"Player 1 Score: {game_state['score1']}", True, BLACK)
    score_text2 = small_font.render(f"Player 2 Score: {game_state['score2']}", True, BLACK)
    win.blit(score_text1, (panel_x + 10, 40))    # Player 1's score on top
    win.blit(score_text2, (panel_x + 10, 70))    # Player 2's score below

    # Display instructions or additional info
    instructions = [
        "Instructions:",
        "- Click a cell to reveal it.",
        "- Find the mine to win!",
        "- Each wrong click reduces your score.",
    ]
    y_offset = 110
    for line in instructions:
        instruction_text = small_font.render(line, True, BLACK)
        win.blit(instruction_text, (panel_x + 10, y_offset))
        y_offset += 20    # Adjusted spacing between lines

    # Display player labels
    player1_text = small_font.render("Player 1: Yellow", True, PALE_YELLOW)
    player2_text = small_font.render("Player 2: Purple", True, LIGHT_PURPLE)
    win.blit(player1_text, (panel_x + 10, y_offset + 20))
    win.blit(player2_text, (panel_x + 10, y_offset + 50))

def check_win(row, col):
    return (row, col) == game_state['mine_location']

def display_game_over(winning_player):
    game_state['game_over'] = True

    # Draw the board to ensure the mine is displayed
    draw_board()

    # Display "Game Over" text with the winning score
    large_font = pygame.font.SysFont(None, 72)
    winning_score = game_state['score1'] if winning_player == 1 else game_state['score2']
    game_over_text = large_font.render(f"Player {winning_player} Wins!", True, SOFT_RED)
    score_text = font.render(f"Winning Score: {winning_score}", True, BLACK)

    # Center the "Game Over" text and score text on the screen
    win.blit(game_over_text, ((WINDOW_WIDTH - game_over_text.get_width()) / 2, BOARD_SIZE / 3))
    win.blit(score_text, ((WINDOW_WIDTH - score_text.get_width()) / 2, BOARD_SIZE / 3 + 80))

    # Draw Restart and Exit buttons
    panel_x = (WINDOW_WIDTH - BUTTON_WIDTH) / 2
    restart_button_y = (BOARD_SIZE / 2) + 50  # Adjusted Y position for Restart button
    exit_button_y = restart_button_y + 70    # Exit button is 70px below Restart button

    pygame.draw.rect(win, SOFT_RED, (panel_x, restart_button_y, BUTTON_WIDTH, BUTTON_HEIGHT))
    restart_text = font.render("Restart", True, BLACK)
    win.blit(restart_text, (panel_x + (BUTTON_WIDTH - restart_text.get_width()) / 2, restart_button_y + 10))

    pygame.draw.rect(win, SOFT_RED, (panel_x, exit_button_y, BUTTON_WIDTH, BUTTON_HEIGHT))
    exit_text = font.render("Exit", True, BLACK)
    win.blit(exit_text, (panel_x + (BUTTON_WIDTH - exit_text.get_width()) / 2, exit_button_y + 10))

    pygame.display.update()

def restart_game():
    global game_state
    game_state = init_game()

def main():
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif not game_state['game_over']:
                draw_board()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    col = event.pos[0] // SQUARE_SIZE
                    row = event.pos[1] // SQUARE_SIZE
                    if event.pos[0] < BOARD_SIZE and game_state['board'][row][col] == '-':  # Ensure click is within board
                        if check_win(row, col):
                            print(f"Player {game_state['current_player']} found the mine! Congratulations, Player {game_state['current_player']} wins!")
                            game_state['game_over'] = True    # Ensure game_over is set to True
                            game_state['last_click'] = (row, col)    # Store the last clicked location
                            display_game_over(game_state['current_player'])
                        else:
                            game_state['board'][row][col] = game_state['current_player']
                            if game_state['current_player'] == 1:
                                game_state['score1'] -= 2
                            else:
                                game_state['score2'] -= 2
                            game_state['current_player'] = 2 if game_state['current_player'] == 1 else 1
            else:
                # Handle game over state and button clicks
                if event.type == pygame.MOUSEBUTTONDOWN:
                    panel_x = (WINDOW_WIDTH - BUTTON_WIDTH) / 2
                    restart_button_y = (BOARD_SIZE / 2) + 50    # Adjusted Y position for Restart button
                    exit_button_y = restart_button_y + 70    # Exit button is 70px below Restart button

                    # Check if Restart button is clicked
                    if restart_button_y <= event.pos[1] <= restart_button_y + BUTTON_HEIGHT:
                        if panel_x <= event.pos[0] <= panel_x + BUTTON_WIDTH:
                            restart_game()
                            draw_board()    # Redraw the board immediately after restarting
                            pygame.display.update()

                    # Check if Exit button is clicked
                    elif exit_button_y <= event.pos[1] <= exit_button_y + BUTTON_HEIGHT:
                        if panel_x <= event.pos[0] <= panel_x + BUTTON_WIDTH:
                            running = False

        pygame.time.Clock().tick(60)    # Increase the frame rate to 60 FPS for smoother updates

    pygame.quit()

if __name__ == "__main__":
    main()