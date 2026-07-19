# ===============
# Definitions
# ===============

# Weighted abstract graph configuration
MANSION_GRAPH = {
    "Study": {"Library": 3, "Hall": 3, "Kitchen": 0},  # 0 cost = Secret Passage
    "Library": {"Study": 3, "Billiard Room": 3},
    "Billiard Room": {"Library": 3, "Conservatory": 3},
    "Conservatory": {
        "Billiard Room": 3,
        "Ballroom": 4,
        "Lounge": 0,
    },  # 0 cost = Secret Passage
    "Ballroom": {"Conservatory": 4, "Kitchen": 4},
    "Kitchen": {"Ballroom": 4, "Dining Room": 3, "Study": 0},  # 0 cost = Secret Passage
    "Dining Room": {"Kitchen": 3, "Lounge": 3},
    "Lounge": {
        "Dining Room": 3,
        "Hall": 4,
        "Conservatory": 0,
    },  # 0 cost = Secret Passage
    "Hall": {"Study": 3, "Lounge": 4},
}
SUSPECTS = [
    "Miss Scarlett",
    "Colonel Mustard",
    "Mrs. White",
    "Reverend Green",
    "Mrs. Peacock",
    "Professor Plum",
]
WEAPONS = ["Candlestick", "Dagger", "Lead Pipe", "Revolver", "Rope", "Wrench"]
ROOMS = list(MANSION_GRAPH.keys())
STARTING_POSITIONS = {
    "Miss Scarlett": "Lounge",
    "Colonel Mustard": "Dining Room",
    "Mrs. White": "Kitchen",
    "Reverend Green": "Ballroom",
    "Mrs. Peacock": "Conservatory",
    "Professor Plum": "Library",
}

# ===============
# Classes / Util Functions
# ===============
import random

MIN_PLAYERS = 3
MAX_PLAYERS = 6


def roll_die() -> int:
    """Roll a single 6 sided die and return int"""
    return random.randint(1, 6)


class Game:
    def __init__(self, num_players: int):
        self.starting_positions = STARTING_POSITIONS
        self.player_turn = 0
        self.players = num_players
        # self.culprit = Suggestion()

    def next_turn(self):
        # run prompts
        # Do you want to move? -> if so run roll and so on
        # Enter room -> make suggestions for room
        # Move the player and weapon
        # Run the suggestion -> letting the user pick which card to show if they have
        # Make accusation!
        # If incorrect, skip turn
        # If correct, you win

        next_player = self.player_turn + 1
        self.player_turn = 0 if next_player > self.players else next_player


class Suggestion:
    def __init__(self, suspect: Player, weapon: str, room: str, players: list[Player]):
        self.suspect = suspect
        self.weapon = weapon
        self.room = room

        suspect.change_room(room)
        for player in players:
            if player.skip:
                continue


class Player:
    def __init__(self, starting_room: str, is_player: bool, skip: bool = False):
        self.location = starting_room
        self.is_player = is_player
        self.skip = skip

    def change_room(self, new_room: str):
        self.location = new_room

    def action_move(self, new_room: str, roll: int):
        pass
        # check roll to the room
        # Check if the room is associated

    def create_suggestion(self, suspect: str, weapon: str, room: str):
        pass
        # move the suspect
        # check the suspect, if any of the players has any of the cards reveal it


# ===============
# Set up
# ===============

# Function to see if use preset or generate random locations
# Function to initialize the game state - make the culprit and distribute the other cards
