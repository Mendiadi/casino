import pygame
import pygame_gui
import requests
import threading

import gui_
import routes


class LoginScreen:
    def __init__(self,gui,adapter):

        self.gui = gui
        self.adapter = adapter
        # Constants
        self.WINDOW_SIZE = (400, 400)
        self.HEADLINE_TEXT = "Welcome"
        self.USER_ID_PLACEHOLDER = "Enter User ID"

        # Create the Pygame window
        pygame.display.set_caption("Login Screen")
        self.window_surface = pygame.display.set_mode(self.WINDOW_SIZE)

        # Create a GUI manager
        self.gui_manager = pygame_gui.UIManager(self.WINDOW_SIZE)

        # Create a background circle
        self.circle_radius = 10
        self.circle_color = (255, 0, 0)
        self.circle_x = -self.circle_radius

        # Create GUI components
        self.headline_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((50, 10), (300, 70)),
            text=self.HEADLINE_TEXT,
            manager=self.gui_manager,
            object_id="headline_label",
        )

        self.user_id_entry = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((50, 100), (300, 40)),
            manager=self.gui_manager,
            object_id="user_id_entry",
        )
        self.user_id_entry.set_text(self.USER_ID_PLACEHOLDER)

        self.login_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((50, 160), (100, 40)),
            text="Login",
            manager=self.gui_manager,
        )

        self.register_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((200, 160), (100, 40)),
            text="Register",
            manager=self.gui_manager,
        )

        # Variable to track if placeholder text is shown
        self.placeholder_shown = True

        # Main loop variables
        self.clock = pygame.time.Clock()
        self.running = True

    def draw(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.gui.running = False
                return
            if self.login_button.rect.collidepoint(pygame.mouse.get_pos()) \
                and event.type == pygame.MOUSEBUTTONDOWN:

                r = requests.post(
                    f"{routes.Routes.prefix}{routes.Routes.host_url}:{routes.Routes.service_session_auth_port}/{routes.Routes.service_session_auth_login}",
                    json={"user_id": self.user_id_entry.get_text()})
                print(r, r.text)
                if r:
                    self.adapter.user_id = self.user_id_entry.get_text()
                    self.gui.current_screen = self.gui.get_lobby_screen()

                    break

            if self.register_button.rect.collidepoint(pygame.mouse.get_pos()) \
                    and event.type == pygame.MOUSEBUTTONDOWN:
                def register():
                    r = requests.post(
                        f"{routes.Routes.prefix}{routes.Routes.host_url}:{routes.Routes.service_session_auth_port}/{routes.Routes.service_session_auth_register}",
                        json={"user_id": self.user_id_entry.get_text()})
                    print(r, r.text)
                    if r.ok:
                        print("register success")
                    else:
                        print(r.text)

                threading.Thread(target=register, daemon=True, name="register").start()

            self.gui_manager.process_events(event)
            # Check if the text entry is focused
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.user_id_entry.rect.collidepoint(event.pos):
                    if self.placeholder_shown:
                        self.user_id_entry.set_text("")
                        self.placeholder_shown = False
            elif event.type == pygame.MOUSEBUTTONUP:
                if not self.user_id_entry.rect.collidepoint(event.pos) and not self.user_id_entry.get_text():
                    self.user_id_entry.set_text(self.USER_ID_PLACEHOLDER)
                    self.placeholder_shown = True

        # Clear the screen
        self.window_surface.fill((0, 0, 0))

        # Move the circle behind the screen
        self.circle_x += 2
        if self.circle_x > self.WINDOW_SIZE[0] + self.circle_radius:
            self.circle_x = -self.circle_radius
        pygame.draw.circle(self.window_surface, self.circle_color, (self.circle_x, 200), self.circle_radius)

        # Update the GUI manager
        self.gui_manager.update(1 / 60.0)

        # Draw the GUI
        self.gui_manager.draw_ui(self.window_surface)

        # Update the display
        pygame.display.update()

        self.clock.tick(60)




# Instantiate and run the LoginScreen
if __name__ == "__main__":
    login_screen = LoginScreen()
    login_screen.mainloop()
