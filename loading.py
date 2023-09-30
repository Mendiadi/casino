import pygame
import sys
import time

import requests

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
TEXT_COLOR = (255, 255, 255)
TEXT_COLOR2 = (255, 0, 255)
FONT_SIZE = 24
display_interval = 0.5  # in seconds

# Initialize the Pygame window
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Text Queue Window")
font = pygame.font.Font(None, FONT_SIZE)
time_line = requests.get("http://127.0.0.1:8080/match", params={"team_a":"s2"
                             ,"team_b":"s"}).json().get("timeline")

text_list = [f"{key.replace(' ','')}: {val}" for key , val in sorted(time_line.items())]
# List to hold the texts
text_list_ordered = []
for t in sorted(text_list):
    print(t if "goal" in t else "")
    text_list_ordered.append(t)
text_list = text_list_ordered
# List to hold the displayed texts
displayed_texts = []
# Function to draw text at left top
def draw_text_left_top(text, color):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.topleft = (10, 10)  # Position at the left top corner
    screen.blit(text_surface, text_rect)
# Function to display texts

def display_texts(texts):
    global display_interval
    screen.fill((0, 0, 0))  # Clear the screen

    for i, text in enumerate(texts):
        if "goal" in text:
            display_interval = 2
            text_surface = font.render(text, True, TEXT_COLOR2)
        else:
            display_interval = 0.3
            text_surface = font.render(text, True, TEXT_COLOR)
        text_rect = text_surface.get_rect()
        text_rect.center = (WINDOW_WIDTH // 2, 50 + i * 50)
        screen.blit(text_surface, text_rect)



# Timer variables
start_time = time.time()
current_time = start_time

total_duration = 30  # in seconds

# Initialize the display with the first 5 texts
displayed_texts = text_list[:1]

# Index for the next text
next_text_index = 1

# Main loop
running = True
while running and current_time - start_time < total_duration:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break

    if current_time - start_time >= display_interval:
        if next_text_index < len(text_list):
            displayed_texts.append(text_list[next_text_index])

            # Check if there are more than 5 displayed texts and remove the oldest one
            if len(displayed_texts) > 5:
                displayed_texts.pop(0)

            next_text_index += 1

        display_texts(displayed_texts)
        start_time = current_time
    draw_text_left_top("GOALS: ",TEXT_COLOR)
    pygame.display.flip()
    current_time = time.time()

# Clean up
pygame.quit()
sys.exit()
