from match_simulation import run_simulation

team_a = "Team A"
team_b = "Team B"
draw = "DRAW"

class Game:
    def __init__(self,name,action,bet,cash_pot):
        self.name = name
        self.action = action
        self.bet = bet
        self.cash_pot = cash_pot
        self.results = None

    def run(self):
        status = run_simulation()
        self.results = self.bet in status["status"]

    def calculate_results(self):
        if self.results:
            print("you win!")
            return self.cash_pot * 2
        else:
            print("you lose!")
            return 0

class Casino:
    def __init__(self):
        self.games = []

        self.balance = 100

    def get_game(self,bet,pot):
        if self.balance >= pot:
            self.balance -= pot
        else:
            return None
        return Game("game1",run_simulation,bet,pot)


def main():
    casino = Casino()
    game = casino.get_game(team_b,20)
    if not game:
        print("balance not enough..")
        return
    game.run()
    casino.balance += game.calculate_results()


if __name__ == '__main__':
    main()