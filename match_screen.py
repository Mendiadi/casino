import threading

import pygame
import pygame_gui

import loading


class GameScreen:
    def __init__(self,gui,adapter):
        # Initialize Pygame
        self.gui = gui
        self.adapter = adapter
        self.screen_width = 800
        self.screen_height = 600
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Player Ready Status")
        self.user = self.adapter.user_id

        # Initialize pygame_gui
        self.gui_manager = pygame_gui.UIManager((self.screen_width, self.screen_height))

        # Create player buttons and input fields
        self.create_player_interface()

    def create_player_interface(self):
        player1_button_rect = pygame.Rect(50, 200, 300, 100)
        player2_button_rect = pygame.Rect(450, 200, 300, 100)

        self.player1_button = pygame_gui.elements.UIButton(
            relative_rect=player1_button_rect,
            text=f"{self.adapter.game[self.user]['p1']} (you)",
            manager=self.gui_manager,
        )
        self.player2_button = pygame_gui.elements.UIButton(
            relative_rect=player2_button_rect,
            text=f"{self.adapter.game[self.user]['p2']}",
            manager=self.gui_manager,
        )

        # Create ready indicators
        self.player1_ready = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(360, 200, 30, 30),
            text="",
            manager=self.gui_manager,
        )
        self.player2_ready = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(760, 200, 30, 30),
            text="",
            manager=self.gui_manager,
        )

        # Create input fields and labels
        input_width = 50
        input_height = 30
        input_padding = 20

        self.player1_goals_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(50, 150, input_width, input_height),
            text="Goals:",
            manager=self.gui_manager,
        )
        self.player1_goals_input = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(50, 180, input_width, input_height),
            manager=self.gui_manager,
        )
        self.player1_assists_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(50 + input_width + input_padding, 150, input_width, input_height),
            text="Assists:",
            manager=self.gui_manager,
        )
        self.player1_assists_input = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(50 + input_width + input_padding, 180, input_width, input_height),
            manager=self.gui_manager,
        )
        self.player1_yellow_cards_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(50 + 2 * (input_width + input_padding), 150, input_width, input_height),
            text="Yellow Cards:",
            manager=self.gui_manager,
        )
        self.player1_yellow_cards_input = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(50 + 2 * (input_width + input_padding), 180, input_width, input_height),
            manager=self.gui_manager,
        )
        self.player1_red_cards_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(50 + 3 * (input_width + input_padding), 150, input_width, input_height),
            text="Red Cards:",
            manager=self.gui_manager,
        )
        self.player1_red_cards_input = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(50 + 3 * (input_width + input_padding), 180, input_width, input_height),
            manager=self.gui_manager,
        )

        self.player2_goals_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(450, 150, input_width, input_height),
            text="Goals:",
            manager=self.gui_manager,
        )
        self.player2_goals_input = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(450, 180, input_width, input_height),
            manager=self.gui_manager,
        )
        self.player2_assists_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(450 + input_width + input_padding, 150, input_width, input_height),
            text="Assists:",
            manager=self.gui_manager,
        )
        self.player2_assists_input = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(450 + input_width + input_padding, 180, input_width, input_height),
            manager=self.gui_manager,
        )
        self.player2_yellow_cards_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(450 + 2 * (input_width + input_padding), 150, input_width, input_height),
            text="Yellow Cards:",
            manager=self.gui_manager,
        )
        self.player2_yellow_cards_input = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(450 + 2 * (input_width + input_padding), 180, input_width, input_height),
            manager=self.gui_manager,
        )
        self.player2_red_cards_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(450 + 3 * (input_width + input_padding), 150, input_width, input_height),
            text="Red Cards:",
            manager=self.gui_manager,
        )
        self.player2_red_cards_input = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(450 + 3 * (input_width + input_padding), 180, input_width, input_height),
            manager=self.gui_manager,
        )

    def draw(self):
        clock = pygame.time.Clock()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.gui.running = False
            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == self.player1_button:
                        self.toggle_ready(self.player1_ready)
                        if not self.adapter.is_waiting_for_start_game:
                            print("adapter run")
                            self.player2_button.set_text(f"waiting for {self.adapter.game[self.user]['p2']} ready")
                            threading.Thread(target=self.adapter.start_game, daemon=True).start()


                    elif event.ui_element == self.player2_button:
                        self.toggle_ready(self.player2_ready)

            self.gui_manager.process_events(event)
        if self.adapter.match:
            self.gui.current_screen = loading.SimulateSrceen(self.gui,self.adapter.match,self.adapter)

            return
        self.gui_manager.update(clock.tick(60) / 1000.0)
        self.screen.fill((0, 0, 0))

        self.gui_manager.draw_ui(self.screen)
        pygame.display.flip()



    def toggle_ready(self, ready_button):
        current_text = ready_button.text
        if current_text == "":
            ready_button.text = "Ready"
        else:
            ready_button.text = ""


if __name__ == "__main__":
    game_screen = GameScreen()
    game_screen.run()
