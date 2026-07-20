import random

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
# List of suspects
SUSPECTS = [
    "Miss Scarlett",
    "Colonel Mustard",
    "Mrs. White",
    "Reverend Green",
    "Mrs. Peacock",
    "Professor Plum",
]
# List of weapons
WEAPONS = ["Candlestick", "Dagger", "Lead Pipe", "Revolver", "Rope", "Wrench"]
# List of rooms
ROOMS = list(MANSION_GRAPH.keys())
# Set starting positions
STARTING_POSITIONS = {
    "Miss Scarlett": "Lounge",
    "Colonel Mustard": "Dining Room",
    "Mrs. White": "Kitchen",
    "Reverend Green": "Ballroom",
    "Mrs. Peacock": "Conservatory",
    "Professor Plum": "Library",
}

# Setting up the min and max player limits
MIN_PLAYERS = 3
MAX_PLAYERS = 6


# ===============
# Support Class Objects
# ===============


class Weapon:
    """Weapon token to track a weapon and its location"""

    def __init__(self, weapon: str):
        self.weapon_name: str = weapon
        self.location: str | None = None

    def get_location(self) -> str:
        """Gets the location of the weapon"""
        if not self.location:
            return "No room"
        return self.location

    def set_location(self, new_room: str) -> None:
        """Changes the location of the weapon"""
        self.location = new_room

    def __str__(self) -> str:
        return f"{self.weapon_name}"


class Player:
    """Player token"""

    def __init__(
        self,
        player_number: int,
        person: str,
        starting_room: str,
        is_player: bool,
        given_cards: list,
        skip: bool = False,
        is_filler: bool = False,
    ):
        self.player_number: int = player_number
        self.person: str = person
        self.location: str = starting_room
        self.is_player: bool = is_player
        self.skip: bool = skip
        self.is_filler: bool = is_filler
        self.hidden_cards: list = given_cards
        self.last_suggested_location: str = ""

    def get_player_identifier(self) -> str:
        """Get player or ai identifier for display purposes"""
        if self.is_filler:
            return f"(Filler) Character {self.person}"
        return f"Player {self.player_number} ({self.person})"

    def change_room(self, new_room: str):
        """Change the room of the player token"""
        self.location = new_room

    def action_move(self, new_room: str, roll: int) -> bool:
        """
        Function for a player to move to a new room while validating possibility.
        Return True for valid move.
        Return False for invalid move.
        """
        current_room = MANSION_GRAPH[self.location]
        # Check if the room is accessible from current
        if new_room not in current_room:
            print("Room selected is not traversable from here\n")
            return False
        # Check if the roll allows for traversal
        new_room_dist = current_room[new_room]
        if roll < new_room_dist:
            print("Not enough distance to travel\n")
            return False
        self.change_room(new_room=new_room)
        print(f"Player {self.person}, you are in {new_room}.")
        return True


class Suggestion:
    def __init__(
        self,
        suspect: str,
        weapon: Weapon,
        room: str,
        player_suggesting: Player | None = None,
        print_buffer: bool = False,
    ):
        self.suspect = suspect
        self.weapon = weapon
        self.room = room
        self.player = player_suggesting
        self.combined_names = [self.room, self.weapon.weapon_name, self.suspect]
        self.print_buffer = print_buffer

    def __str__(self) -> str:
        return f"{self.suspect}, with the {self.weapon}, in the {self.room}"

    def compare_suggestions(self, to_compare: "Suggestion") -> bool:
        """Compare two suggestions to see if the contents match exactly"""
        return (
            self.suspect == to_compare.suspect
            and self.weapon.weapon_name == to_compare.weapon.weapon_name
            and self.room == to_compare.room
        )

    def declare_suggestion(
        self, players: dict[str, Player], current_player: Player, player_turn: int
    ):
        """Function that allows a player to trigger the user flow for a suggestion"""
        suspect_player = players[self.suspect]
        suspect_player.change_room(self.room)
        if suspect_player.last_suggested_location != self.room:
            suspect_player.last_suggested_location = ""
        self.weapon.set_location(new_room=self.room)
        if current_player.last_suggested_location == self.room:
            print("You cannot suggest in the same room in a row")

        players_objs = list(players.values())
        # Reorder the reveal order to the next index and skip current player
        reveal_order_players = (
            players_objs[player_turn + 1 :] + players_objs[:player_turn]
        )
        for player in reveal_order_players:
            # Check if the player has at least one hidden card and not current player
            if (
                len(player.hidden_cards) < 1
                or player.player_number == current_player.player_number
            ):
                continue
            # Checks if cards are shared with suggestion
            cards = self.player_check_cards(revealing_player=player)
            # If it has no matching cards, continue
            if cards is None:
                continue
            # Handle current player updates
            current_player.last_suggested_location = self.room
            # Reveal the card to the current player
            if player.is_player:
                self.player_reveal_card(
                    matching_cards=cards, player_id=player.get_player_identifier()
                )
                return
            # For now, reveal card for non players is always first one
            self.reveal_card(
                player_id=player.get_player_identifier(), revealed_card=cards[0]
            )
            return
        print("No other players have any cards related to suggestion.")

    def player_check_cards(
        self,
        revealing_player: Player,
    ) -> list | None:
        """
        Check a player's hand to see if they have a card (intended for a player).
        Return list of matching cards else None
        """
        # Cross reference the current suggestion with a player's cards
        matching_cards = list(
            set(self.combined_names) & set(revealing_player.hidden_cards)
        )
        if len(matching_cards) == 0:
            print(f"{revealing_player.get_player_identifier()} passes.")
            return
        return matching_cards

    def reveal_card(self, player_id: str, revealed_card: str) -> None:
        """Support function to just print what was revealed"""
        print(f"{player_id} revealed {revealed_card}, click enter to continue")

    def player_reveal_card(self, matching_cards: list, player_id: str):
        """Lets a player select the card they want to reveal to another player and reveals it"""
        input(
            f"{player_id} has at least 1 card, provide control to the player and click enter."
        )
        if self.print_buffer:
            print_screen_buffer()
        print(
            f"{player_id}, the current player suggested {self}, choose one to reveal, after return to original player"
        )
        revealed_card = list_options(matching_cards)
        if self.print_buffer:
            print_screen_buffer()
        self.reveal_card(player_id=player_id, revealed_card=revealed_card)


# ===============
# Classes / Util Functions
# ===============


def list_options(options: list, prompt: str = ""):
    """Print out the current options and request the user to chose one, return the result"""
    print()
    if prompt:
        print(prompt)
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
    """Print a screen buffer to prevent players from seeing the hot swap"""
    print("\n" * 50)


def roll_die() -> int:
    """Roll a single 6 sided die and return int"""
    return random.randint(1, 6)


def player_roll_die() -> int:
    """Provide a prompt to roll a die"""
    input("Press enter to roll your die!")
    return roll_die()


class Game:
    def __init__(self, num_players: int, num_bots: int, print_buffer: bool = True):
        self.player_turn = 0
        self.num_players = num_players
        self.num_bots = num_bots
        self.players: dict[str, Player] = {}
        self.print_buffer = print_buffer
        self.weapons: dict[str, Weapon] = {w: Weapon(w) for w in WEAPONS}
        self.shared_cards_str: str = ""

        # Generate the final accusation on initialization
        final_suspect = random.choice(SUSPECTS)
        final_weapon = random.choice(list(self.weapons.values()))
        final_room = random.choice(ROOMS)
        self.final_accusation = Suggestion(
            suspect=final_suspect,
            room=final_room,
            weapon=final_weapon,
            print_buffer=self.print_buffer,
        )

    def game_setup(self):
        initial_players: dict[str, Player | None] = dict.fromkeys(SUSPECTS)

        # Generate and shuffle the deck
        full_deck = SUSPECTS + WEAPONS + ROOMS
        filtered_deck = [
            item
            for item in full_deck
            if item
            not in [
                self.final_accusation.weapon.weapon_name,
                self.final_accusation.suspect,
                self.final_accusation.room,
            ]
        ]
        random.shuffle(filtered_deck)
        cards_per_player = len(filtered_deck) // self.num_players

        # Let people choose their characters
        available_suspects = SUSPECTS.copy()
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
            filtered_deck = filtered_deck[cards_per_player:]
            initial_players[chosen_suspect] = Player(
                player_number=i,
                person=chosen_suspect,
                starting_room=STARTING_POSITIONS[chosen_suspect],
                is_player=True,
                given_cards=player_deck_hand,
            )

        # Generate the remaining suspects
        for suspect, suspect_obj in initial_players.items():
            if suspect_obj is None:
                initial_players[suspect] = Player(
                    player_number=-1,
                    person=suspect,
                    starting_room=STARTING_POSITIONS[suspect],
                    is_player=False,
                    given_cards=[],
                    skip=True,
                )
        # Line for coercing the typing from dict[str, Player | None] to dict[str, Player], but functionality should be fine
        self.players = {x: y for x, y in initial_players.items() if y is not None}
        if len(self.players) != 6:
            raise ValueError("The total characters is not 6")
        if len(filtered_deck) > 0:
            temp_str = ", ".join(filtered_deck)
            print(f"Shared remaining deck: {temp_str}")
            self.shared_cards_str = temp_str

    def get_player_from_index(self) -> Player:
        """Using the current turn counter, get the player object"""
        current_player_character = SUSPECTS[self.player_turn]
        return self.players[current_player_character]

    def check_accusation(self, accusation: Suggestion) -> bool:
        """Run a check for an accusation, return if the user won"""
        if not self.final_accusation:
            raise RuntimeError("Missing final accusation")
        is_correct = self.final_accusation.compare_suggestions(accusation)
        player_ref = accusation.player
        if player_ref is None:
            raise RuntimeError("Player is missing in accusation")
        if is_correct:
            print(
                f"{player_ref.get_player_identifier()} has made a correct accusation with {accusation}!"
            )
            return True
        print_screen_buffer()
        print(
            f"{player_ref.get_player_identifier()} has made an incorrect accusation and will now be skipped."
        )
        # If the player is incorrect, mark as skip
        player_ref.skip = True
        return False

    def take_turn(self, current_player: Player) -> bool | None:
        """Acts as a turn for a player. Returns if the the user won or None"""
        # run prompts
        player_id = current_player.get_player_identifier()
        if current_player.skip:
            print(f"skipping {player_id}")
            return
        player_location = current_player.location
        changed_locations = False
        print(f"{player_id}, you are in the {player_location}")
        input("Click enter when ready.")
        hidden_card_str = ", ".join(current_player.hidden_cards)
        print(f"Hidden cards: {hidden_card_str}")
        if self.shared_cards_str:
            print(f"Shared cards: {self.shared_cards_str}")
        is_in_last_suggestion = (
            current_player.last_suggested_location == player_location
        )
        # Do you want to move? -> if so run roll and so on
        want_to_move = None
        while True:
            if is_in_last_suggestion:
                print(
                    "Note: you will not be able to make a suggestion in the same room twice"
                )
            temp_ans = input("Do you want to move? (y/n) ")
            if temp_ans.lower() in ["y", "n"]:
                want_to_move = temp_ans.lower() == "y"
                break
            print("Please enter y/Y for yes or n/N for no")
        if want_to_move:
            die_res = player_roll_die()
            print(f"{player_id} rolled a {die_res}")
            possible_rooms = [
                f"{location}-({dist} distance)"
                for location, dist in MANSION_GRAPH[player_location].items()
            ]
            possible_rooms.append("Stay")
            while True:
                move_choice = list_options(
                    options=possible_rooms,
                    prompt=f"Choose a room to travel to, ensure you can travel the distance. 0 are secret passages - Current roll {die_res}",
                )
                # If staying, move forward
                if move_choice == "Stay":
                    break
                # Ensure the player can move, if so update the player
                if current_player.action_move(
                    new_room=move_choice.split("-")[0], roll=die_res
                ):
                    player_location = current_player.location
                    changed_locations = True
                    break

        # Enter room -> make suggestions for room
        possible_actions = ["make accusation"]
        if not is_in_last_suggestion or changed_locations:
            possible_actions.insert(0, "make suggestion")
        # If the same location, allow to end turn - assuming the user cannot move out or if they want to make an accusation
        if not changed_locations:
            possible_actions.append("end turn")
        action_in_room = list_options(
            options=possible_actions,
            prompt=f"{player_id} what would you like to do in this room?",
        )
        if action_in_room == "end turn":
            return
        # Run the suggestion -> letting the user pick which card to show if they have
        suspect = list_options(options=SUSPECTS, prompt="What person do you suspect?")
        weapon = list_options(options=WEAPONS, prompt="What weapon do you suspect?")
        room = player_location
        player_suggestion = Suggestion(
            suspect=suspect,
            weapon=self.weapons[weapon],
            room=room,
            player_suggesting=current_player,
            print_buffer=self.print_buffer,
        )
        print(f"{player_id} suggest it was {player_suggestion}")
        current_player.last_suggested_location = room
        # Make accusation
        if action_in_room == "make accusation":
            return self.check_accusation(accusation=player_suggestion)
        # If not accusation, then do a normal suggestion check
        player_suggestion.declare_suggestion(
            players=self.players,
            current_player=current_player,
            player_turn=self.player_turn,
        )

    def end_turn(self):
        """Change the turn / player"""
        # Update turn according to the length of suspects
        next_player = self.player_turn + 1
        self.player_turn = 0 if next_player >= len(SUSPECTS) else next_player
        curr_player = self.get_player_from_index()
        # If player is skipped, then continue to the next player
        if curr_player.skip:
            print(f"Skipping {curr_player.get_player_identifier()}")
            self.end_turn()

    def play(self):
        """Run the game"""
        self.game_setup()
        print("Finished game set up\n\n\n")
        while True:
            # Get player object, based on suspect order
            current_player = self.get_player_from_index()
            # Play turn
            result = self.take_turn(current_player=current_player)
            if result == True:
                break
            if all([p.skip for p in self.players.values()]):
                print("All players have failed to find the suspect. Game ending.")
                break
            input(
                f"To end your turn {current_player.get_player_identifier()}, click enter."
            )
            self.end_turn()
            if self.print_buffer:
                print_screen_buffer()


# ===============
# Set up
# ===============


def main():
    num_players = 0
    # Prompts for game set up
    while True:
        try:
            num_players = int(
                input(
                    f"Provide the number of players between {MIN_PLAYERS} to {MAX_PLAYERS}: "
                )
            )
        except ValueError:
            print(f"Please input a valid integer from {MIN_PLAYERS} to {MAX_PLAYERS}")
            continue
        if num_players >= MIN_PLAYERS and num_players <= MAX_PLAYERS:
            break
    print_buffer = True
    print_buffer = (
        input(
            "Would you like to use screen buffer (hides results from other players)? Type NO to remove, else yes: "
        ).lower()
        != "no"
    )
    # For part 1, number of bots will be forced to 0
    game = Game(num_players=num_players, num_bots=0, print_buffer=print_buffer)
    game.play()


if __name__ == "__main__":
    main()
