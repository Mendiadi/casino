import pygame
import sys
import time
import routes
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
time_line = requests.get(f"{routes.Routes.prefix}{routes.Routes.host_url}:{routes.Routes.service_simulator_port}/{routes.Routes.service_simulator_match}", params={"team_a":"s2"
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

def draw_text(offset_y,offset_x,text,color):
    text_surface = font.render(text, False, color)
    text_rect = text_surface.get_rect()
    text_rect.topleft = (offset_x, offset_y)  # Position at the left top corner
    screen.blit(text_surface, text_rect)

def format_match_data():
    # {"teamname":{goals:0,assists:0,"yellow":0,red:0}}
    ...

def draw_texts(color,data=None):
    draw_text(5,10,"TEAM: ",color)
    draw_text(35,10, "Goals: ", color)
    draw_text(75,10, "Assists: ", color)
    draw_text(105,10, "Yellow Cards: ", color)
    draw_text(135,10, "Red Cards: ", color)
    draw_text(5,580,"TEAM: ",color)
    draw_text(35,580, "Goals: ", color)
    draw_text(75,580, "Assists: ", color)
    draw_text(105,580, "Yellow Cards: ", color)
    draw_text(135,580, "Red Cards: ", color)
# Function to display texts

def display_texts(texts):
    global display_interval
    screen.fill((0, 0, 0))  # Clear the screen

    for i, text in enumerate(texts):
        if "goal" in text:
            display_interval = 2
            text_surface = font.render(text, True, TEXT_COLOR2)
        elif "yellow" in text:
            display_interval = 1
            text_surface = font.render(text, True, (255,255,0))
        elif "red" in text:
            display_interval = 1
            text_surface = font.render(text, True,  (255, 0, 0))

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
    draw_texts(TEXT_COLOR)
    pygame.display.flip()
    current_time = time.time()

# Clean up
pygame.quit()
sys.exit()
