import pygame
import sys
import time

import game_screen
import routes
import requests

# Initialize Pygam
class SimulateSrceen():
    def __init__(self,gui,game,adapter):
        self.adapter = adapter
        self.game =game
        self.gui = gui
    # pygame.init()
    # Constants

        self.WINDOW_WIDTH = 800
        self.WINDOW_HEIGHT = 600
        self.TEXT_COLOR = (255, 255, 255)
        self.TEXT_COLOR2 = (255, 0, 255)
        self.FONT_SIZE = 24
        self.display_interval = 0.5  # in seconds

        # Initialize the Pygame window
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        pygame.display.set_caption("Text Queue Window")
        self.font = pygame.font.Font(None, self.FONT_SIZE)

        self.time_line = self.game.get("timeline")

        self.text_list = [f"{key.replace(' ','')}: {val}" for key , val in sorted(self.time_line.items())]
        # List to hold the texts
        self.text_list_ordered = []
        for t in sorted(self.text_list):
            print(t if "goal" in t else "")
            self.text_list_ordered.append(t)
        self.text_list = self.text_list_ordered
        # List to hold the displayed texts
        self.displayed_texts = []
        # Timer variables
        self.start_time = time.time()
        self.current_time = self.start_time

        self.total_duration = 35  # in seconds

        # Initialize the display with the first 5 texts
        self.displayed_texts = self.text_list[:1]
        self.simulate_done = False
        # Index for the next text
        self.next_text_index = 1
        # Function to draw text at left top

    def draw_text(self,offset_y,offset_x,text,color):
        text_surface = self.font.render(text, False, color)
        text_rect = text_surface.get_rect()
        text_rect.topleft = (offset_x, offset_y)  # Position at the left top corner
        self.screen.blit(text_surface, text_rect)

    def format_match_data(data):
        # {"teamname":{goals:0,assists:0,"yellow":0,red:0}}
        ...

    def draw_texts(self,color,data=None):
        self.draw_text(5,10,f"TEAM:  ",color)
        self.draw_text(35,10, f"Goals: {len(list(filter(lambda x: self.adapter.user_id in x,self.game.get('goals',0))))}", color)
        self.draw_text(75,10, f"Assists: ", color)
        self.draw_text(105,10, "Yellow Cards: ", color)
        self.draw_text(135,10, "Red Cards: ", color)
        self.draw_text(5,580,"TEAM: ",color)
        self.draw_text(35,580, f"Goals: {len(list(filter(lambda x: self.adapter.user_id not in x,self.game.get('goals',0))))}", color)
        self.draw_text(75,580, "Assists: ", color)
        self.draw_text(105,580, "Yellow Cards: ", color)
        self.draw_text(135,580, "Red Cards: ", color)
    # Function to display texts

    def display_texts(self,texts):
        self.screen.fill((0, 0, 0))  # Clear the screen

        for i, text in enumerate(texts):
            if "goal" in text:
                self.display_interval = 2
                self.text_surface = self.font.render(text, True, self.TEXT_COLOR2)
            elif "yellow" in text:
                self.display_interval = 1
                self.text_surface = self.font.render(text, True, (255,255,0))
            elif "red" in text:
                self.display_interval = 1
                self.text_surface = self.font.render(text, True,  (255, 0, 0))

            else:
                self.display_interval = 0.3
                self.text_surface = self.font.render(text, True, self.TEXT_COLOR)

            self.text_rect = self.text_surface.get_rect()
            self.text_rect.center = (self.WINDOW_WIDTH // 2, 50 + i * 50)
            self.screen.blit(self.text_surface, self.text_rect)




    def draw(self):
    # Main loop

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.gui.running = False
                break

        if  self.current_time -  self.start_time >=  self.display_interval:
            if  self.next_text_index < len( self.text_list):
                self.displayed_texts.append( self.text_list[ self.next_text_index])

                # Check if there are more than 5 displayed texts and remove the oldest one
                if len( self.displayed_texts) > 5:
                    self. displayed_texts.pop(0)

                self.next_text_index += 1

            self.display_texts(self.displayed_texts)
            self.start_time = self.current_time
        print(int(str(int(self.current_time))[len(str(int(self.current_time))):]))
        # if int(str(int(self.current_time))[len(str(int(self.current_time))):]) > self.total_duration:
        #     self.gui.current_screen = self.gui.get_lobby_screen()
        #     self.adapter = game_screen.Adapter(self.adapter.user_id)
        #     return
        self.draw_texts(self.TEXT_COLOR)
        pygame.display.flip()
        self.current_time = time.time()

    # Clean up


