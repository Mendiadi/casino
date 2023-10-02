import pygame
import pygame_gui
import random

# Initialize pygame
pygame.init()

# Define screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Create the Pygame screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Casino Lobby")

# Initialize pygame_gui
# pygame_gui.init()

# Create a manager for the GUI elements
gui_manager = pygame_gui.UIManager((SCREEN_WIDTH, SCREEN_HEIGHT))

# Define colors
WHITE = (255, 255, 255)
BACKGROUND_COLOR = (0, 128, 0)

# Create background surface
background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
background.fill(BACKGROUND_COLOR)

# Create a font for the headline
headline_font = pygame.font.Font(None, 72)
headline_text = headline_font.render("Casino", True, WHITE)

# Load images for casino games
slot_machine_image = pygame.image.load(r"C:\Users\adim\PycharmProjects\gui_project\world\assets\money.png")  # Replace with your image
roulette_table_image = pygame.image.load(r"C:\Users\adim\PycharmProjects\gui_project\world\assets\money.png")  # Replace with your image

# Create buttons for casino games
slot_machine_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect(100, 100, 200, 100),
    text="Play PVP",
    manager=gui_manager,
)
roulette_table_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect(400, 100, 200, 100),
    text="About us",
    manager=gui_manager,
)

# Animation variables
game_objects = []


def create_game_object(image):
    x = random.randint(50, SCREEN_WIDTH - 50)
    y = random.randint(-200, -50)
    speed = random.randint(1, 3)
    return {"image": image, "rect": pygame.Rect(x, y, 100, 100), "speed": speed}


game_objects.append(create_game_object(slot_machine_image))
game_objects.append(create_game_object(roulette_table_image))

# Headline animation variables
headline_x = 350
headline_y = 20
headline_speed = 1

# Main loop
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Process GUI events
        gui_manager.process_events(event)

    # Update animations
    for game_object in game_objects:
        game_object["rect"].move_ip(0, game_object["speed"])
        if game_object["rect"].top > SCREEN_HEIGHT:
            game_objects.remove(game_object)
            game_objects.append(create_game_object(game_object["image"]))

    headline_x += headline_speed
    if headline_x > SCREEN_WIDTH:
        headline_x = -headline_text.get_width()

    gui_manager.update(clock.tick(60) / 1000.0)

    screen.blit(background, (0, 0))

    for game_object in game_objects:
        screen.blit(game_object["image"], game_object["rect"])

    screen.blit(headline_text, (headline_x, headline_y))

    gui_manager.draw_ui(screen)

    pygame.display.flip()

# Quit Pygame
pygame.quit()
