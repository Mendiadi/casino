import pygame
import sys


def run():
    # internal data
    AMOUNT_OF_POT = 0

    # external data
    BALANCE_VALUE = 1000

    # Constants
    WIDTH, HEIGHT = 800, 600
    BACKGROUND_COLOR = (0, 128, 0)
    TEXT_COLOR = (255, 255, 255)
    BUTTON_COLOR = (255, 0, 0)
    SLIDER_COLOR = (0, 0, 255)

    # Initialize Pygame
    pygame.init()
    # Create the screen
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("CASINO")

    # Define fonts
    font = pygame.font.Font(None, 36)

    # Player profile content
    current_player_profile = f"Player: John Doe\nBalance: ${BALANCE_VALUE}"

    # Create the "Start Game" button rect
    start_button = pygame.Rect(300, 250, 200, 50)

    # Flag to control the second window
    show_second_window = False

    # Flag to control the bonus window
    show_bonus_window = False

    # Flag to control slider interaction
    slider_dragging = False

    # Slider properties
    slider_min = 0
    slider_max = 100
    slider_value = slider_min

    # Bonus window entries and values
    bonus_entries = [0, 0, 0, 0]
    bonus_entry_rects = []

    def draw_home_screen():
        screen.fill(BACKGROUND_COLOR)

        # Draw player profile label
        profile_label = font.render(current_player_profile, True, TEXT_COLOR)
        screen.blit(profile_label, (20, 20))

        # Draw the "Start Game" button
        pygame.draw.rect(screen, BUTTON_COLOR, start_button)
        start_text = font.render("Start Game", True, TEXT_COLOR)
        screen.blit(start_text, (350, 260))

        pygame.display.flip()

        # Function to draw the second window

    def draw_second_window():
        screen.fill(BACKGROUND_COLOR)

        # Draw header
        header_text = font.render("Choose", True, TEXT_COLOR)
        screen.blit(header_text, (350, 20))
        header_text = font.render(f"BALANCE: ${BALANCE_VALUE - AMOUNT_OF_POT}", True, TEXT_COLOR)
        screen.blit(header_text, (350 - header_text.get_width() // 2, 80))
        header_text = font.render(f"POT: ${AMOUNT_OF_POT}", True, TEXT_COLOR)
        screen.blit(header_text, (350 - header_text.get_width() // 2, 450))
        # Draw three buttons
        button_width = 150
        button_height = 50
        button_spacing = 20
        for i in range(3):
            button_rect = pygame.Rect(100 + i * (button_width + button_spacing), 150, button_width, button_height)
            pygame.draw.rect(screen, BUTTON_COLOR, button_rect)
            button_text = font.render(f"Button {i + 1}", True, TEXT_COLOR)
            screen.blit(button_text, (button_rect.centerx - button_text.get_width() // 2, 160))

        # Draw the slider bounds line
        pygame.draw.line(screen, SLIDER_COLOR, (350, 530), (450, 530), 5)

        # Draw the slider button
        slider_button = pygame.Rect(350 + (slider_value / slider_max) * 100, 500, 30, 30)
        pygame.draw.rect(screen, BUTTON_COLOR, slider_button)

        pygame.display.flip()

    # Function to draw the bonus window
    def draw_bonus_window():
        screen.fill(BACKGROUND_COLOR)

        # Draw header
        header_text = font.render("Choose Bonus", True, TEXT_COLOR)
        screen.blit(header_text, (350 - header_text.get_width() // 2, 20))
        header_text = font.render(f"BALANCE: ${BALANCE_VALUE}", True, TEXT_COLOR)
        screen.blit(header_text, (350 - header_text.get_width() // 2, 80))

        # Draw entries
        entry_height = 50
        entry_spacing = 20
        texts = ("Goals", "Assists", "Red Cards", "Yellow Cards")
        for i in range(len(texts)):
            entry_rect = pygame.Rect(300, 150 + i * (entry_height + entry_spacing), 200, entry_height)
            pygame.draw.rect(screen, TEXT_COLOR, entry_rect, 2)
            entry_text = font.render(texts[i], True, TEXT_COLOR)
            screen.blit(entry_text,
                        (entry_rect.x - entry_text.get_width() - 10, entry_rect.centery - entry_text.get_height() // 2))
            n_str = str(bonus_entries[i])
            if len(n_str) > 3:
                n_str = n_str[:3]
                bonus_entries[i] = int(n_str)
            entry_input_text = font.render(n_str, True, TEXT_COLOR)
            screen.blit(entry_input_text, (entry_rect.x + 10, entry_rect.centery - entry_input_text.get_height() // 2))

        # Draw the "Start" button
        start_bonus_button = pygame.Rect(350 - 75, 400, 150, 50)
        pygame.draw.rect(screen, BUTTON_COLOR, start_bonus_button)
        start_bonus_text = font.render("Start", True, TEXT_COLOR)
        screen.blit(start_bonus_text, (350 - start_bonus_text.get_width() // 2, 410))

        pygame.display.flip()

    # Main game loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(event.pos):
                    # Toggle the second window
                    show_second_window = not show_second_window
                elif show_second_window:
                    for i in range(3):
                        button_rect = pygame.Rect(100 + i * (150 + 20), 150, 150, 50)
                        if button_rect.collidepoint(event.pos):
                            # Show the bonus window when clicking a button
                            show_bonus_window = True
                            break
                    if show_bonus_window:
                        for i, entry_rect in enumerate(bonus_entry_rects):
                            if entry_rect.collidepoint(event.pos):
                                # Activate the clicked bonus entry for editing
                                active_bonus_entry = i

                                break
                    # Check for slider interaction
                    if 350 <= event.pos[0] <= 450 and 500 <= event.pos[1] <= 530:
                        slider_dragging = True
            if event.type == pygame.MOUSEBUTTONUP:
                slider_dragging = False
                active_bonus_entry = None
            if event.type == pygame.MOUSEMOTION and slider_dragging:
                x, _ = event.pos
                x = max(350, min(x, 450))  # Constrain slider within bounds
                slider_value = int(((x - 350) / 100) * (slider_max - slider_min) + slider_min)
                AMOUNT_OF_POT = slider_value
            if event.type == pygame.KEYDOWN and show_bonus_window and active_bonus_entry is not None:
                print(type(active_bonus_entry))
                if event.key == pygame.K_BACKSPACE:
                    bonus_entries[active_bonus_entry] = int(bonus_entries[active_bonus_entry] / 10)
                elif event.key in [pygame.K_0, pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6,
                                   pygame.K_7, pygame.K_8, pygame.K_9]:
                    digit = int(event.unicode)
                    bonus_entries[active_bonus_entry] = bonus_entries[active_bonus_entry] * 10 + digit

        if show_second_window:
            if show_bonus_window:
                if not bonus_entry_rects:
                    entry_height = 50
                    entry_spacing = 20
                    for i in range(4):
                        entry_rect = pygame.Rect(300, 150 + i * (entry_height + entry_spacing), 200, entry_height)
                        bonus_entry_rects.append(entry_rect)
                draw_bonus_window()
            else:
                draw_second_window()
        else:
            draw_home_screen()

    # Quit Pygame
    pygame.quit()
    sys.exit()
