import threading

import pygame
import sys

import requests

import gui_

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 400, 300
BACKGROUND_COLOR = (255, 255, 255)
BUTTON_COLOR = (50, 50, 50)
TEXT_COLOR = (255, 255, 255)
FONT = pygame.font.Font(None, 32)
USER_ID = ""

# Create the main window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Login Window")


# Function to draw the login window
def draw_login_window():
    screen.fill(BACKGROUND_COLOR)

    # Draw the user ID input box
    pygame.draw.rect(screen, BUTTON_COLOR, (100, 100, 200, 40))
    pygame.draw.rect(screen, TEXT_COLOR, (100, 100, 200, 40), 2)

    # Draw the register button
    pygame.draw.rect(screen, BUTTON_COLOR, (100, 160, 200, 40))
    register_text = FONT.render("Register", True, TEXT_COLOR)
    screen.blit(register_text, (155, 170))

    # Draw the login button
    pygame.draw.rect(screen, BUTTON_COLOR, (100, 220, 200, 40))
    login_text = FONT.render("Login", True, TEXT_COLOR)
    screen.blit(login_text, (175, 230))

    # Display the user ID text
    user_text = FONT.render(USER_ID, True, TEXT_COLOR)
    screen.blit(user_text, (110, 110))


# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                USER_ID = USER_ID[:-1]
            else:
                USER_ID += event.unicode
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if 100 <= event.pos[0] <= 300:
                if 160 <= event.pos[1] <= 200:
                    # Add code to handle register button click and redirection here
                    print("Register button clicked")
                    r = requests.post("http://127.0.0.1:9090/register", json={"user_id": USER_ID})
                    print(r, r.text)
                    if r.ok:
                        print("register sucess")
                    else:
                        print(r.text)
                elif 220 <= event.pos[1] <= 260:
                    # Add code to handle login button click and redirection here
                    print("User ID:", USER_ID)
                    r = requests.post("http://127.0.0.1:9090/login", json={"user_id": USER_ID})
                    print(r, r.text)
                    if r:
                        pygame.quit()
                        threading.Thread(target=gui_.run,args=(USER_ID,)).start()

                        running = False
                        break
                    else:
                        user_text = FONT.render("user already logged in", True, TEXT_COLOR)
                        screen.blit(user_text, (10, 10))
    if running:
        draw_login_window()
        pygame.display.update()
