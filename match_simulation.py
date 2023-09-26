import gym
import random

# Constants
NUM_PLAYERS_PER_TEAM = 11
MATCH_DURATION = 90  # minutes
PLAYER_ENERGY_MAX = 100
GOAL_PROBABILITY = 0.05  # Probability of scoring a goal
ASSIST_PROBABILITY = 0.3  # Probability of an assist
YELLOW_CARD_PROBABILITY = 0.05  # Probability of a yellow card
RED_CARD_PROBABILITY = 0.02  # Probability of a red card
MAX_YELLOW_CARDS = 2
ENERGY_REDUCTION_RATE = 0.5  # Base energy reduction rate per minute
POSITION_ENERGY_REDUCTION = {"Forward": 0.2, "Midfielder": 0.15, "Defender": 0.1}  # Energy reduction by position


class SoccerEnv(gym.Env):
    def __init__(self):
        super(SoccerEnv, self).__init__()
        self.team_a = self._init_team("Team A",(60,90))
        self.team_b = self._init_team("Team B",(60,90))
        self.current_minute = 0
        self.team_switch_momentum = 0.5  # Initial momentum value
        self.yellow_cards = {}
        self.red_cards = {}
        self.goals = {}
        self.assists = {}

    def _calculate_team_switch_probability(self, team_a_goals, team_b_goals, player_ratings):
        # Calculate the team switch probability based on player ratings and match statistics
        team_a_score = sum(player["goals_scored"] for player in self.team_a)
        team_b_score = sum(player["goals_scored"] for player in self.team_b)

        # Calculate team ratings based on player ratings
        team_a_rating = sum(player_ratings["Team A"]) / NUM_PLAYERS_PER_TEAM
        team_b_rating = sum(player_ratings["Team B"]) / NUM_PLAYERS_PER_TEAM

        # Calculate the momentum factor based on match score
        momentum_factor = (team_a_score - team_b_score) / max(team_a_score, team_b_score, 1)

        # Calculate the switch probability
        switch_probability = (team_b_rating - team_a_rating) / 100 + momentum_factor + self.team_switch_momentum

        # Cap the switch probability between 0 and 1
        switch_probability = min(1, max(0, switch_probability))

        return switch_probability

    def _init_team(self, name,rate):
        team = []
        for i in range(NUM_PLAYERS_PER_TEAM):
            player = {
                "name": f"{name} Player {i + 1}",
                "rating": random.randint(*rate),
                "energy": PLAYER_ENERGY_MAX,
                "goals_scored": 0,
                "position": random.choice(["Forward", "Midfielder", "Defender"]),
            }
            team.append(player)
        return team

    def _calculate_goal_probability(self, player):
        # Adjust goal-scoring probability based on player's rating and energy
        return (GOAL_PROBABILITY * player["rating"] / 100) * (player["energy"] / PLAYER_ENERGY_MAX)

    def _calculate_assist_probability(self, player):
        # Adjust assist probability based on player's rating and energy
        return (ASSIST_PROBABILITY * player["rating"] / 100) * (player["energy"] / PLAYER_ENERGY_MAX)

    def _print_match_info(self, minute, team_with_ball, leading_team):
        print(f"minute {minute:02d}:00: {team_with_ball} has the ball, {leading_team} leading")

    def _take_action(self, team, minute):
        player_with_ball = random.choice(team)
        return player_with_ball

    def step(self, action):
        team_with_ball = random.choice(("Team A","Team B"))
        if self.current_minute >= MATCH_DURATION:
            team_a_goals = sum(player["goals_scored"] for player in self.team_a)
            team_b_goals = sum(player["goals_scored"] for player in self.team_b)
            print(f"Match ended. Final score: Team A {team_a_goals} - {team_b_goals} Team B")

            if team_a_goals > team_b_goals:
                print("Team A wins!")
                status = "Team A win"
            elif team_b_goals > team_a_goals:
                print("Team B wins!")
                status = "Team B win"
            else:
                print("It's a draw!")
                status = "DRAW"
            return True, {"status": status}

        team_a_score = sum(player["goals_scored"] for player in self.team_a)
        team_b_score = sum(player["goals_scored"] for player in self.team_b)

        player_ratings = {"Team A": [player["rating"] for player in self.team_a],
                          "Team B": [player["rating"] for player in self.team_b]}

        # Calculate team switch probability
        switch_probability = self._calculate_team_switch_probability(team_a_score, team_b_score, player_ratings)

        # Determine the team with the ball based on the switch probability
        if random.random() < switch_probability:
            team_with_ball = "Team B" if team_with_ball == "Team A" else "Team A"
        leading_team = "Team A" if sum(player["goals_scored"] for player in self.team_a) > sum(
            player["goals_scored"] for player in self.team_b
        ) else "Team B"

        player_with_ball = self._take_action(self.team_a if team_with_ball == "Team A" else self.team_b,
                                             self.current_minute)

        # Reduce player energy based on their activity and position
        for player in self.team_a + self.team_b:
            player["energy"] -= ENERGY_REDUCTION_RATE

            if player == player_with_ball:
                player["energy"] -= ENERGY_REDUCTION_RATE  # Additional energy reduction for having the ball

            # Reduce energy based on player's position
            position_energy_reduction = POSITION_ENERGY_REDUCTION.get(player["position"], 0)
            player["energy"] -= position_energy_reduction

            # Ensure energy doesn't go below zero
            player["energy"] = max(0, player["energy"])

        if random.random() < self._calculate_goal_probability(player_with_ball):
            scoring_team = self.team_a if team_with_ball == "Team A" else self.team_b
            scorer = random.choice(scoring_team)
            scorer["goals_scored"] += 1
            if scorer["name"] in self.goals:
                self.goals[scorer["name"]] += 1
            else:
                self.goals[scorer["name"]] = 1
            if random.random() < self._calculate_assist_probability(player_with_ball):
                assisting_player = random.choice(scoring_team)
                if assisting_player["name"] in self.assists:
                    self.assists[assisting_player["name"]] +=1
                else:
                    self.assists[assisting_player["name"]] = 1

                print(
                    f"minute {self.current_minute:02d}:45: {scorer['name']} scores a goal, assisted by {assisting_player['name']} for {team_with_ball}")
            else:
                print(f"minute {self.current_minute:02d}:45: {scorer['name']} scores a goal for {team_with_ball}")
        elif random.random() < YELLOW_CARD_PROBABILITY:
            player = player_with_ball
            if player["name"] in self.yellow_cards:
                self.yellow_cards[player["name"]] += 1
                if self.yellow_cards[player["name"]] == MAX_YELLOW_CARDS:
                    print(
                        f"minute {self.current_minute:02d}:30: {player['name']} receives a red card and is sent off for {team_with_ball}")
                    self.yellow_cards.pop(player["name"])  # Remove the player from the yellow card list
                    team_with_card = self.team_a if team_with_ball == "Team A" else self.team_b
                    team_with_card.remove(player)
                else:
                    print(
                        f"minute {self.current_minute:02d}:30: {player['name']} receives a yellow card for {team_with_ball}")
            else:
                self.yellow_cards[player["name"]] = 1
                print(
                    f"minute {self.current_minute:02d}:30: {player['name']} receives a yellow card for {team_with_ball}")

        elif random.random() < RED_CARD_PROBABILITY:
            team_with_card = self.team_a if team_with_ball == "Team A" else self.team_b
            player_with_card = random.choice(team_with_card)
            print(
                f"minute {self.current_minute:02d}:30: {player_with_card['name']} receives a red card and is sent off for {team_with_ball}")
            team_with_card.remove(player_with_card)
            if player_with_card["name"] not in self.red_cards:
                self.red_cards[player_with_card["name"]] = 1
            else:
                self.red_cards[player_with_card["name"]] += 1


        else:
            player_with_ball = self._take_action(self.team_a if team_with_ball == "Team A" else self.team_b,
                                                 self.current_minute)
            print(
                f"minute {self.current_minute:02d}:30: {player_with_ball['name']} has the ball, {leading_team} leading")

        self.current_minute += 1

        return False, {"status":f"processing {self.current_minute}"}

    def reset(self):
        self.team_a = self._init_team("Team A")
        self.team_b = self._init_team("Team B")
        self.current_minute = 0
        return None

    def render(self):
        pass

    def close(self):
        pass


def run_simulation():
    env = SoccerEnv()
    done = False
    print("TEAMS BEFORE MATCH")
    print("*"*200)
    print("TEAM A")
    print(env.team_a)
    print("*" * 200)
    print("TEAM B")
    print(env.team_b)
    print("*" * 200)
    while not done:
        done, status = env.step(None)
    print("Match ended.")
    print(status["status"])
    print("*" * 200)
    print("ASSISTS")
    print(env.assists)
    print("*" * 200)
    print("RED CARDS")
    print(env.red_cards)
    print("*" * 200)
    print("YELLOW CARDS")
    print(env.yellow_cards)
    print("*" * 200)
    print("GOALS")
    print(env.goals)
    print("TEAMS AFTER MATCH")
    print("*" * 200)
    print("TEAM A")
    print(env.team_a)
    print("*" * 200)
    print("TEAM B")
    print(env.team_b)
    print("*" * 200)
    return status

run_simulation()

# Main
# if __name__ == "__main__":
#     games = []
#     for i in range(20):
#         status = run_simulation()
#         games.append(status["status"])
#     print("*"*200)
#     total = {"A":0,"B":0,"Draw":0}
#     for s in games:
#         if "Team B" in s:
#             total["B"] +=1
#         elif "Team A" in s:
#             total["A"] +=1
#         else:
#             total["Draw"] +=1
#     print(total)
