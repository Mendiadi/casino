import threading
import time
import routes
import pygame
import sys

import requests

# Initialize Pygame

slider_min = 0
slider_max = 100
slider_dragging = False
AMOUNT_OF_POT = 0
slider_value = 0
bonus_entries = [0, 0, 0, 0]
bonus_entry_rects = []
start_bonus_button = pygame.Rect(350 - 75, 500, 150, 50)
active_bonus_entry = False
back_button = pygame.Rect(300, 250, 200, 50)


# loading_font = pygame.font.Font(None, 36)
def run(user_id):
    def update_user_data():
        time.sleep(5)
        global BALANCE_VALUE
        BALANCE_VALUE = int(requests.get(f"{routes.Routes.prefix}{routes.Routes.host_url}:{routes.Routes.service_pay_port}/{routes.Routes.service_pay_balance}",
                                         params={"user_id": user_id}).text)

    # internal data

    # external data
    BALANCE_VALUE = int(requests.get(f"{routes.Routes.prefix}{routes.Routes.host_url}:{routes.Routes.service_pay_port}/{routes.Routes.service_pay_balance}",
                                     params={"user_id": user_id}).text)
    pygame.init()
    # Constants
    WIDTH, HEIGHT = 800, 600
    BACKGROUND_COLOR = (0, 128, 0)
    TEXT_COLOR = (255, 255, 255)
    BUTTON_COLOR = (255, 0, 0)
    SLIDER_COLOR = (0, 0, 255)

    # Create the screen
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("CASINO")

    # Define fonts
    font = pygame.font.Font(None, 36)

    # Player profile content
    current_player_profile = f"Welcome Back: {user_id}{' ' * 15}Your Balance: ${BALANCE_VALUE}"

    # Create the "Start Game" button rect
    start_button = pygame.Rect(300, 250, 200, 50)

    # Create a font for displaying text

    # Get the current time

    def process_loading():
        if not Handler.trigger_loading:
            Handler.title_text = "CASINO"
            pygame.display.set_caption(Handler.title_text)
        else:
            Handler.title_text = "waiting for other player..."
            pygame.display.set_caption(Handler.title_text)

    class Handler:
        next_event_handler = None
        next_screen_handler = None
        current_screen_handler = None
        current_event_handler = None
        trigger_loading = False
        title_text = ""

    class Adapter:
        def __init__(self):
            self.reset()

        def reset(self):
            self.is_waiting_for_start_game = False
            self.is_searching = False
            self.game = None
            self.match = None

        def get_game(self, online=True):
            if not self.is_searching:
                r = requests.get(f"{routes.Routes.prefix}{routes.Routes.host_url}:{routes.Routes.service_casino_port}/{routes.Routes.service_casino_game}",
                                 params={"p1": user_id, "action": 2, "bet": 2,
                                         "cash_pot": 500, "p2": online})
                if r.ok:
                    self.is_searching = True
                    res = "OK"
                    Handler.trigger_loading = True

                    while res.lower() == "ok" or len(r.json()) < 5:

                        time.sleep(0.5)

                        r = requests.get(f"{routes.Routes.prefix}{routes.Routes.host_url}:{routes.Routes.service_casino_port}/{routes.Routes.service_casino_game}",
                                         params={"p1": user_id, "action": 2, "bet": 2,
                                                 "cash_pot": 500, "p2": online})
                        print(r, r.text)
                        if r.ok:
                            res = r.text
                    self.is_searching = False
                    Handler.trigger_loading = False
                    self.game = r.json()


        def start_game(self):
            if not self.is_waiting_for_start_game:
                print("inside adapter")
                r = requests.post(f"{routes.Routes.prefix}{routes.Routes.host_url}:{routes.Routes.service_casino_port}/{routes.Routes.service_casino_game}",
                                  json={"user_id": user_id, "team": user_id})
                Handler.trigger_loading = True

                if r.ok:
                    self.is_waiting_for_start_game = True
                    res = "OK"
                    while res.lower() == "ok":
                        print("adapter loop")
                        time.sleep(0.5)
                        r = requests.post(f"{routes.Routes.prefix}{routes.Routes.host_url}:{routes.Routes.service_casino_port}/{routes.Routes.service_casino_game}",
                                          json={"user_id": user_id, "team": user_id})
                        print(r, r.text)
                        if r.ok:
                            res = r.text
                    if res == "user_left":
                        adapter.reset()
                        Handler.current_screen_handler = draw_home_screen
                        Handler.current_event_handler = welcome_window_events_handler
                        Handler.title_text = "user left the game"
                        Handler.trigger_loading = False
                        return
                    self.is_waiting_for_start_game = False
                    self.match = r.json()
                    Handler.trigger_loading = False
                    update_user_data()

    adapter = Adapter()

    def get_match_headline():
        if adapter.match:
            return f"match result : {adapter.match['status']}"
        return "wait for player 2 be ready.."

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

    def draw_versus_screen():
        screen.fill(BACKGROUND_COLOR)

        # Draw player profile label
        profile_label = font.render(current_player_profile, True, TEXT_COLOR)
        screen.blit(profile_label, (20, 20))
        versus_label = font.render(get_match_headline(), True, TEXT_COLOR)
        screen.blit(versus_label, (20, 60))

        # Draw the "Start Game" button
        pygame.draw.rect(screen, BUTTON_COLOR, back_button)
        start_text = font.render("back", True, TEXT_COLOR)
        screen.blit(start_text, (350, 260))

        pygame.display.flip()

    def get_game_text():
        if adapter.game:
            for game in adapter.game:
                if type(adapter.game[game]) is dict:
                    if adapter.game[game].get("p1", None) and game != user_id:
                        return f"you play VS {game}"
        return "wait for game.."

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
        for i in range(1):
            button_rect = pygame.Rect(100 + i * (button_width + button_spacing), 150, button_width, button_height)
            pygame.draw.rect(screen, BUTTON_COLOR, button_rect)
            button_text = font.render(f"Play Online {i + 1}", True, TEXT_COLOR)
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
        header_text_2 = font.render(get_game_text(), True, TEXT_COLOR)
        screen.blit(header_text_2, (350 - header_text_2.get_width() // 2, 50))
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
        if adapter.game:
            pygame.draw.rect(screen, BUTTON_COLOR, start_bonus_button)
            start_bonus_text = font.render("Start", True, TEXT_COLOR)
            screen.blit(start_bonus_text, (350 - start_bonus_text.get_width() // 2, 510))
        if not bonus_entry_rects:
            entry_height = 50
            entry_spacing = 20
            for i in range(4):
                entry_rect = pygame.Rect(300, 150 + i * (entry_height + entry_spacing), 200, entry_height)
                bonus_entry_rects.append(entry_rect)
        pygame.display.flip()

    def versus_window_events_handler(event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if start_button.collidepoint(event.pos):
                # Toggle the second window
                adapter.reset()
                Handler.current_screen_handler = draw_home_screen
                Handler.current_event_handler = welcome_window_events_handler

    def second_window_events_handler(event):
        global AMOUNT_OF_POT, slider_dragging, slider_value, slider_max, slider_min

        if event.type == pygame.MOUSEBUTTONDOWN:
            for i in range(1):
                button_rect = pygame.Rect(100 + i * (150 + 20), 150, 150, 50)
                if button_rect.collidepoint(event.pos):
                    # Show the bonus window when clicking a button
                    if not adapter.is_searching:
                        threading.Thread(target=adapter.get_game, daemon=True).start()
                    Handler.current_screen_handler = draw_bonus_window
                    Handler.current_event_handler = bonus_window_events_handler

                    break
            if 350 <= event.pos[0] <= 450 and 500 <= event.pos[1] <= 530:
                slider_dragging = True
        if event.type == pygame.MOUSEBUTTONUP:
            slider_dragging = False
        if event.type == pygame.MOUSEMOTION and slider_dragging:
            x, _ = event.pos
            x = max(350, min(x, 450))  # Constrain slider within bounds
            slider_value = int(((x - 350) / 100) * (slider_max - slider_min) + slider_min)
            AMOUNT_OF_POT = slider_value

    def bonus_window_events_handler(event):
        global active_bonus_entry, bonus_entries, bonus_entry_rects
        if event.type == pygame.MOUSEBUTTONDOWN:

            if start_bonus_button.collidepoint(event.pos):

                if not adapter.is_waiting_for_start_game:
                    print("adapter run")
                    threading.Thread(target=adapter.start_game, daemon=True).start()
                    Handler.current_event_handler = versus_window_events_handler
                    Handler.current_screen_handler = draw_versus_screen

            for i, entry_rect in enumerate(bonus_entry_rects):
                if entry_rect.collidepoint(event.pos):
                    # Activate the clicked bonus entry for editing
                    active_bonus_entry = i
                    break
        if event.type == pygame.KEYDOWN and active_bonus_entry is not None:
            if event.key == pygame.K_BACKSPACE:
                bonus_entries[active_bonus_entry] = int(bonus_entries[active_bonus_entry] / 10)
            elif event.key in [pygame.K_0, pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6,
                               pygame.K_7, pygame.K_8, pygame.K_9]:
                digit = int(event.unicode)
                bonus_entries[active_bonus_entry] = bonus_entries[active_bonus_entry] * 10 + digit

    def welcome_window_events_handler(event):

        if event.type == pygame.MOUSEBUTTONDOWN:
            if start_button.collidepoint(event.pos):
                # Toggle the second window
                Handler.current_screen_handler = draw_second_window
                Handler.current_event_handler = second_window_events_handler

    # Main game loop
    running = True
    Handler.current_event_handler = welcome_window_events_handler
    Handler.current_screen_handler = draw_home_screen
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                r = requests.put(f"{routes.Routes.prefix}{routes.Routes.host_url}:{routes.Routes.service_session_auth_port}/{routes.Routes.service_session_auth_logout}", json={"user_id": user_id})
                print(r, r.text)
                break
            Handler.current_event_handler(event)
        Handler.current_screen_handler()
        process_loading()
    # Quit Pygame
    pygame.quit()
    sys.exit()
