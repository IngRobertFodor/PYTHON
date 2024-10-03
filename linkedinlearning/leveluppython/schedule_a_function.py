import time
# !!! RUN THIS FIRST (CMD)
# pip install pygame
import pygame # type: ignore


def play_sound(when_to_play, filename_to_play, print_msg):
    
    print("Press Enter to start the sound in: ", when_to_play, "seconds")
    input()
    time.sleep(when_to_play)
    print(print_msg)

    # Initialize Pygame
    pygame.init()
    # Load the MP3 file
    pygame.mixer.music.load(filename_to_play)
    # Play the MP3 file
    pygame.mixer.music.play()
    # Keep the program running to let the music play
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(15)

    return 


play_sound(5, "cat_meow.mp3", "Cat Sounds")