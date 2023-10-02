import pygame
import pygame_gui
import random



class CasinoLobby:

    def create_game_object(self,image):
        x = random.randint(50, self.SCREEN_WIDTH - 50)
        y = random.randint(-200, -50)
        speed = random.randint(1, 3)
        return {"image": image, "rect": pygame.Rect(x, y, 100, 100), "speed": speed}
    def __init__(self):
        pygame.init()

        # Define screen dimensions
        self.SCREEN_WIDTH = 800
        self.SCREEN_HEIGHT = 600

        # Create the Pygame screen
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("Casino Lobby")

        # Create a manager for the GUI elements
        self.gui_manager = pygame_gui.UIManager((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))

        # Define colors
        self.WHITE = (255, 255, 255)
        self.BACKGROUND_COLOR = (0, 128, 0)

        # Create background surface
        self.background = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        self.background.fill(self.BACKGROUND_COLOR)

        # Create a font for the headline
        self.headline_font = pygame.font.Font(None, 72)
        self.headline_text = self.headline_font.render("Casino", True, self.WHITE)

        # Load images for casino games
        self.slot_machine_image = pygame.image.load(
            r"C:\Users\adim\PycharmProjects\gui_project\world\assets\money.png")  # Replace with your image
        self.roulette_table_image = pygame.image.load(
            r"C:\Users\adim\PycharmProjects\gui_project\world\assets\money.png")  # Replace with your image

        # Create buttons for casino games
        self.slot_machine_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(100, 100, 200, 100),
            text="Play PVP",
            manager=self.gui_manager,
        )
        self.roulette_table_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(400, 100, 200, 100),
            text="About us",
            manager=self.gui_manager,
        )

        # Animation variables
        self.game_objects = []

        def create_game_object(image):
            x = random.randint(50, self.SCREEN_WIDTH - 50)
            y = random.randint(-200, -50)
            speed = random.randint(1, 3)
            return {"image": image, "rect": pygame.Rect(x, y, 100, 100), "speed": speed}

        self.game_objects.append(create_game_object(self.slot_machine_image))
        self.game_objects.append(create_game_object(self.roulette_table_image))

        # Headline animation variables
        self.headline_x = 350
        self.headline_y = 20
        self.headline_speed = 1

        # Main loop variables
        self.running = True
        self.clock = pygame.time.Clock()
    def draw(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            # Process GUI events
            self.gui_manager.process_events(event)

        # Update animations
        for game_object in self.game_objects:
            game_object["rect"].move_ip(0, game_object["speed"])
            if game_object["rect"].top > self.SCREEN_HEIGHT:
                self.game_objects.remove(game_object)
                self.game_objects.append(self.create_game_object(game_object["image"]))

        self.headline_x += self.headline_speed
        if self.headline_x > self.SCREEN_WIDTH:
            self.headline_x = -self.headline_text.get_width()

        self.gui_manager.update(self.clock.tick(60) / 1000.0)

        self.screen.blit(self.background, (0, 0))

        for game_object in self.game_objects:
            self.screen.blit(game_object["image"], game_object["rect"])

        self.screen.blit(self.headline_text, (self.headline_x, self.headline_y))

        self.gui_manager.draw_ui(self.screen)

        pygame.display.flip()
    def mainloop(self):
        while self.running:
            self.draw()

        # Quit Pygame
        pygame.quit()


# Instantiate and run the CasinoLobby
if __name__ == "__main__":
    casino_lobby = CasinoLobby()
    casino_lobby.mainloop()
