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


def list_options(options: list):
    """Print out the current options and request the user to chose one, return the result"""
    print("Please type the number for the action you would like:")
    for i in range(1, len(options) + 1):
        print(f"({i}) {options[i - 1]}")
    while True:
        chosen = input("Chosen option: ")
        try:
            chosen = int(chosen)
        except ValueError:
            print("Invalid option, please type an integer")
            continue
        if chosen < 1 or chosen > len(options):
            print(f"Value must between 1 and {len(options)}")
            continue
        return options[chosen - 1]


def print_screen_buffer() -> None:
    print("\n" * 10)


def roll_die() -> int:
    """Roll a single 6 sided die and return int"""
    return random.randint(1, 6)


class Game:
    def __init__(self, num_players: int, num_bots: int):
        self.player_turn = 0
        self.num_players = num_players
        self.num_bots = num_bots
        self.players = dict.fromkeys(SUSPECTS)
        self.final_accusation = None

    def game_setup(self):
        # Generate the final accusation
        final_suspect = random.choice(SUSPECTS)
        final_weapon = random.choice(WEAPONS)
        final_room = random.choice(ROOMS)
        self.final_accusation = Suggestion(
            suspect=final_suspect, room=final_room, weapon=final_weapon
        )

        # Generate and shuffle the deck
        full_deck = SUSPECTS + WEAPONS + ROOMS
        filtered_deck = [
            item
            for item in full_deck
            if item not in [final_weapon, final_suspect, final_room]
        ]
        random.shuffle(filtered_deck)
        cards_per_player = len(filtered_deck) // self.num_players

        # Let people choose their characters
        available_suspects = SUSPECTS
        for i in range(1, self.num_players + 1):
            is_bot = i > self.num_players - self.num_bots
            if not is_bot:
                print(f"Player {i}, please choose a suspect to play as")
                chosen_suspect = list_options(list(available_suspects))
            else:
                print(f"Player {i} is a bot")
                chosen_suspect = random.choice(available_suspects)

            available_suspects.remove(chosen_suspect)
            player_deck_hand = filtered_deck[:cards_per_player]
            cards_per_player = filtered_deck[cards_per_player:]
            self.players[chosen_suspect] = Player(
                player_number=i,
                person=chosen_suspect,
                starting_room=STARTING_POSITIONS[chosen_suspect],
                is_player=True,
                given_cards=player_deck_hand,
            )

        # Wrap up if all 6 players are already assigned
        if self.num_players == 6:
            return

        # Generate the remaining suspects
        for suspect, suspect_obj in self.players.items():
            if suspect_obj is not None:
                continue
            self.players[suspect] = Player(
                player_number=-1,
                person=suspect,
                starting_room=STARTING_POSITIONS[suspect],
                is_player=False,
                given_cards=[],
                skip=True,
            )

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
        self.player_turn = 0 if next_player > self.num_players else next_player


class Suggestion:
    def __init__(self, suspect: str, weapon: str, room: str):
        self.suspect = suspect
        self.weapon = weapon
        self.room = room
        self.combined = [self.room, self.weapon, self.suspect]

    def declare_suggestion(self, players: dict):
        suspect_player = players[self.suspect]
        suspect_player.change_room(self.room)
        for player in players:
            if player.skip:
                continue
            cards = self.player_check_cards(revealing_player=player)
            if cards is None:
                continue
            if player.is_player:
                self.player_reveal_card(
                    matching_cards=cards, player_id=player.player_identifier()
                )
                break
            # For now, reveal card for non players is always first one
            self.reveal_card(
                player_id=player.player_identifier(), revealed_card=cards[0]
            )
            break

        print("No players have any cards related to suggestion.")

    def player_check_cards(
        self,
        revealing_player: Player,
    ) -> list | None:
        """
        Check a player's hand to see if they have a card (intended for a player).
        Return list of matching cards else None
        """
        # Cross reference the current suggestion with a player's cards
        matching_cards = list(set(self.combined) & set(revealing_player.hidden_cards))
        if len(matching_cards) == 0:
            print(f"Player {revealing_player.player_identifier()} passes.")
            return
        return matching_cards

    def reveal_card(self, player_id: str, revealed_card: str) -> None:
        """Support function to just print what was revealed"""
        input(
            f"Player {player_id} revealed {revealed_card}, click enter to continue and end your turn"
        )
        print_screen_buffer()

    def player_reveal_card(self, matching_cards: list, player_id: str):
        """Lets a player select the card they want to reveal to another player and reveals it"""
        input(
            f"Player {player_id} has at least 1 card, provide control to the player and click enter."
        )
        print(
            f"Player {player_id}, the current player suggested {self.combined}, choose one to reveal, after return to original player"
        )
        revealed_card = list_options(matching_cards)
        print_screen_buffer()
        self.reveal_card(player_id=player_id, revealed_card=revealed_card)


class Player:
    def __init__(
        self,
        player_number: int,
        person: str,
        starting_room: str,
        is_player: bool,
        given_cards: list,
        skip: bool = False,
    ):
        self.player_number = player_number
        self.person = person
        self.location = starting_room
        self.is_player = is_player
        self.skip = skip
        self.hidden_cards = given_cards

    def player_identifier(self) -> str:
        return f"Player {self.player_number} ({self.person})"

    def change_room(self, new_room: str):
        self.location = new_room

    def action_move(self, new_room: str, roll: int) -> bool:
        """
        Function for a player to move to a new room while validating possibility.
        Return True for valid move.
        Return False for invalid move.
        """
        current_room = MANSION_GRAPH[self.location]
        if new_room not in current_room:
            print("Room selected is not traversable")
            return False
        new_room_dist = current_room[new_room]
        if new_room_dist < roll:
            print("Not enough distance to travel")
            return False
        self.change_room(new_room=new_room)
        print(f"Player {self.person}, you are in {new_room}.")
        return True


# ===============
# Set up
# ===============

# Function to see if use preset or generate random locations
# Function to initialize the game state - make the culprit and distribute the other cards


def main():
    num_players = 0
    while True:
        try:
            num_players = int(
                input(
                    f"Provide the number of players between {MIN_PLAYERS} to {MAX_PLAYERS}:"
                )
            )
        except ValueError:
            print(f"Please input a valid integer from {MIN_PLAYERS} to {MAX_PLAYERS}")
            continue
        if num_players >= MIN_PLAYERS and num_players <= MAX_PLAYERS:
            break
    # For part 1, number of bots will be forced to 0
    game = Game(num_players=num_players, num_bots=0)
