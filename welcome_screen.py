import threading

import pygame
import pygame_gui
import requests

import gui_
import routes

# Initialize Pygame
pygame.init()

# Constants
WINDOW_SIZE = (400, 400)
HEADLINE_TEXT = "Welcome"
USER_ID_PLACEHOLDER = "Enter User ID"

# Create the Pygame window
pygame.display.set_caption("Login Screen")
window_surface = pygame.display.set_mode(WINDOW_SIZE)

# Create a GUI manager
gui_manager = pygame_gui.UIManager(WINDOW_SIZE)

# Create a background circle
circle_radius = 10
circle_color = (255, 0, 0)
circle_x = -circle_radius

# Create GUI components
headline_label = pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect((50,10), (300, 70)),
    text=HEADLINE_TEXT,
    manager=gui_manager,
    object_id="headline_label",
)
  # Increase the font size

user_id_entry = pygame_gui.elements.UITextEntryLine(
    relative_rect=pygame.Rect((50, 100), (300, 40)),
    manager=gui_manager,
    object_id="user_id_entry",
)
user_id_entry.set_text(USER_ID_PLACEHOLDER)

login_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((50, 160), (100, 40)),
    text="Login",
    manager=gui_manager,
)

register_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((200, 160), (100, 40)),
    text="Register",
    manager=gui_manager,
)

# Variable to track if placeholder text is shown
placeholder_shown = True

# Main loop
clock = pygame.time.Clock()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == login_button:
                    r = requests.post(
                        f"{routes.Routes.prefix}{routes.Routes.host_url}:{routes.Routes.service_session_auth_port}/{routes.Routes.service_session_auth_login}",
                        json={"user_id": user_id_entry.get_text()})
                    print(r, r.text)
                    if r:
                        pygame.quit()
                        threading.Thread(target=gui_.run,args=(user_id_entry.get_text(),)).start()

                        running = False
                        break
                elif event.ui_element == register_button:
                    def register():

                        r = requests.post(
                            f"{routes.Routes.prefix}{routes.Routes.host_url}:{routes.Routes.service_session_auth_port}/{routes.Routes.service_session_auth_register}",
                            json={"user_id": user_id_entry.get_text()})
                        print(r, r.text)
                        if r.ok:
                            print("register sucess")
                        else:
                            print(r.text)
                    threading.Thread(target=register, daemon=True, name="register").start()

        gui_manager.process_events(event)

        # Check if the text entry is focused
        if event.type == pygame.MOUSEBUTTONDOWN:
            if user_id_entry.rect.collidepoint(event.pos):
                if placeholder_shown:
                    user_id_entry.set_text("")
                    placeholder_shown = False
        elif event.type == pygame.MOUSEBUTTONUP:
            if not user_id_entry.rect.collidepoint(event.pos) and not user_id_entry.get_text():
                user_id_entry.set_text(USER_ID_PLACEHOLDER)
                placeholder_shown = True

    # Clear the screen


    # Move the circle behind the screen
    circle_x += 2
    if circle_x > WINDOW_SIZE[0] + circle_radius:
        circle_x = -circle_radius
    pygame.draw.circle(window_surface, circle_color, (circle_x, 200), circle_radius)

    # Update the GUI manager
    gui_manager.update(1 / 60.0)

    # Draw the GUI
    gui_manager.draw_ui(window_surface)

    # Update the display
    pygame.display.update()

    clock.tick(60)

# Quit Pygame
pygame.quit()
