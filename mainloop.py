import pygame
import requests

import game_screen,screens,welcome_screen
import routes


class GUI:

    def __init__(self):
        pygame.init()
        self.adapter = game_screen.Adapter("")
        self.current_screen = self.get_welcome_screen()
        self.running = True

    def get_welcome_screen(self):
        return welcome_screen.LoginScreen(self,self.adapter)

    def get_lobby_screen(self):
        return screens.CasinoLobby(self)

    def get_game_screen(self):
        return  game_screen.GameScreen(self,self.adapter)
    def mainloop(self):
        while self.running:
            self.current_screen.draw()

        # Quit Pygame
        pygame.quit()
        r = requests.put(
            f"{routes.Routes.prefix}{routes.Routes.host_url}:{routes.Routes.service_session_auth_port}/{routes.Routes.service_session_auth_logout}",
            json={"user_id": self.adapter.user_id})
        print(r, r.text)

if __name__ == '__main__':
    GUI().mainloop()