import threading

import pygame
import pygame_gui
import requests
import time
import routes


def update_user_data(user_id):
    time.sleep(5)
    BALANCE_VALUE = int(requests.get(
        f"{routes.Routes.prefix}{routes.Routes.host_url}:{routes.Routes.service_pay_port}/{routes.Routes.service_pay_balance}",
        params={"user_id": user_id}).text)
    return BALANCE_VALUE
class Adapter:
    def __init__(self,user_id):
        self.reset()
        self.user_id = user_id
        self.balance = "1000"
    def reset(self):
        self.is_waiting_for_start_game = False
        self.is_searching = False
        self.game = None
        self.match = None


    def get_game(self, online=True):
        if self.game:
            return
        if not self.is_searching:

            r = requests.get(
                f"{routes.Routes.prefix}{routes.Routes.host_url}:{routes.Routes.service_casino_port}/{routes.Routes.service_casino_game}",
                params={"p1": self.user_id, "action": 2, "bet": 2,
                        "cash_pot": 500, "p2": online})
            if r.ok:
                self.is_searching = True
                res = "OK"
                # Handler.trigger_loading = True

                while res.lower() == "ok" or len(r.json()) < 5:

                    time.sleep(0.5)

                    r = requests.get(
                        f"{routes.Routes.prefix}{routes.Routes.host_url}:{routes.Routes.service_casino_port}/{routes.Routes.service_casino_game}",
                        params={"p1": self.user_id, "action": 2, "bet": 2,
                                "cash_pot": 500, "p2": online})
                    print(r, r.text)
                    if r.ok:
                        res = r.text
                self.is_searching = False
                # Handler.trigger_loading = False
                self.game = r.json()

    def start_game(self):
        if not self.is_waiting_for_start_game:
            print("inside adapter")
            r = requests.post(
                f"{routes.Routes.prefix}{routes.Routes.host_url}:{routes.Routes.service_casino_port}/{routes.Routes.service_casino_game}",
                json={"user_id": self.user_id, "team": self.user_id, "p2": self.game[self.user_id]['p2']})
            # Handler.trigger_loading = True

            if r.ok:
                self.is_waiting_for_start_game = True
                res = "OK"
                while res.lower() == "ok":
                    print("adapter loop")
                    time.sleep(0.5)
                    r = requests.post(
                        f"{routes.Routes.prefix}{routes.Routes.host_url}:{routes.Routes.service_casino_port}/{routes.Routes.service_casino_game}",
                        json={"user_id": self.user_id, "team": self.user_id, "p2": self.game[self.user_id]['p2']})
                    print(r, r.text)
                    if r.ok:
                        res = r.text
                if res == "user_left":
                    # adapter.reset()
                    # Handler.current_screen_handler = draw_home_screen
                    # Handler.current_event_handler = welcome_window_events_handler
                    # Handler.title_text = "user left the game"
                    # Handler.trigger_loading = False
                    return
                self.is_waiting_for_start_game = False
                self.match = r.json()
                # Handler.trigger_loading = False
                self.balance = update_user_data(self.user_id)
class GameScreen:
    def __init__(self,gui,adapter):
        self.adapter = adapter
        self.gui = gui
        self.window_size = (800, 600)
        self.window = pygame.display.set_mode(self.window_size)
        self.manager = pygame_gui.UIManager(self.window_size)
        self.clock = pygame.time.Clock()
        self.is_running = True
        self.balance = self.adapter.balance
        self.user_id = self.adapter.user_id
        self.loading_progress = 0
        self.loading_duration = 3.0  # Time in seconds for the loading animation
        self.loading_timer = None
        self.dot_effect = "..."

        self.create_elements()

    def create_elements(self):
        # Create the "Match 500$" button
        button_rect = pygame.Rect(100, 200, 600, 100)
        self.match_button = pygame_gui.elements.UIButton(
            relative_rect=button_rect,
            text="Match 500$",
            manager=self.manager,
        )

        # Create the headline label
        self.headline_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(300, 50, 200, 50),
            text="Choose Match",
            manager=self.manager,
        )

        # Create the balance label
        self.balance_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(20, 20, 250, 30),
            text=f'Your Balance: ${self.balance}',
            manager=self.manager,
        )

        # Create the user ID label
        self.user_id_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(20, 60, 250, 30),
            text=f'User ID: {self.user_id}',
            manager=self.manager,
        )

    def start_loading_animation(self):
        self.loading_progress = 0
        self.match_button.disable()
        self.loading_timer = pygame.time.get_ticks()
        pygame.time.set_timer(pygame.USEREVENT, int(self.loading_duration * 1000 / 100))

    def update_loading_animation(self):

        elapsed_time = pygame.time.get_ticks() - self.loading_timer
        self.loading_progress = int((elapsed_time / (self.loading_duration * 1000)) * 100)
        if self.loading_progress in range(100,999):
            if int(str(self.loading_progress)[0]) % 2 == 0:
                print(self.loading_progress)
                self.match_button.set_text(f"Loading{self.dot_effect} {self.loading_progress}%")
            else:
                self.match_button.set_text(f"looking for match{self.dot_effect} {self.loading_progress}%")
        elif self.loading_progress > 1000:
            self.match_button.set_text(f"we almost there{self.dot_effect} {self.loading_progress}%")

        else:
            self.match_button.set_text(f"Loading{self.dot_effect} {self.loading_progress}%")

        if not self.adapter.is_searching:
            pygame.time.set_timer(pygame.USEREVENT, 0)
            self.match_button.enable()
            if self.adapter.game:
                self.match_button.set_text(f"game found VS {self.adapter.game[self.user_id]['p2']}")
                self.loading_timer = None


    def draw(self):
        time_delta = self.clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.gui.running = False
                return
            if self.match_button.rect.collidepoint(pygame.mouse.get_pos()) \
                    and event.type == pygame.MOUSEBUTTONDOWN:

                self.start_loading_animation()
                print("hey")
                if not self.adapter.is_searching:
                    threading.Thread(target=self.adapter.get_game, daemon=True).start()


            self.manager.process_events(event)

        if self.loading_timer is not None:
            self.match_button.disable()
            self.update_loading_animation()


        self.manager.update(time_delta)
        self.window.fill((0, 0, 0))

        self.manager.draw_ui(self.window)

        pygame.display.flip()


if __name__ == "__main__":
    game_screen = GameScreen(Adapter("dd"))

