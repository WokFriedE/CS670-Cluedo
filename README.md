# Cludeo

Ethan Ho | ekh3
CS 670 - 850
Project 2, Part 1
<ekh3@njit.edu>

## Quick Start

1. Clone the repository.
   1. ```git clone https://github.com/WokFriedE/CS670-Cluedo```
2. In the root of the code, run the command ```python3 EthanHo_Project2_SourceCode/cluedo.py``` to run the game.

## Game Setup

When trying to start the game, run the following command:

```python3
python3 EthanHo_Project2_SourceCode/cluedo.py 
```

The game will then prompt the user in the CLI several questions including:

1. How many players?
   1. This will have to be between 3 and 6 players.
2. Would you like to use the screen buffer?
   1. This will ensure each play will have some screen buffer so players cant see other players' information.

The game will then set up the rest:

- It would create choose the accusation cards.
- Remove the accusation cards, shuffle and distribute to the remaining players.
- Turn the remaining suspects (which are not players) into placeholders.
- If the remaining cards do not evenly split between players, it will display the remaining shared cards.

## General Comments

- Have to keep track of your own evidence and shared cards, but your hidden cards.
- Assumes hot swapping so there will be screen buffers to prevent players from seeing sensitive data, but you can disable the screen buffer during set up phases.
- Currently for part 1 of the project, it does not allow bots.
- Most of the application will prompt users to enter their choices by choosing a choice with numbers or yes and no prompts.

## General Rules

- Have to be in a room to make a suggestion.
- When you enter a room during your turn you must make a suggestion or accusation.
- If you enter a room from another player, you are given the option to stay and make a suggestion.
- Cannot make suggestion in the same room twice, but you can make one if you were moved into the room.
- Accusations have to be in the same room, but can be made without conditions in your turn.
- When revealing cards, it will be in suspect order with the next player being checked first.
- Since we are using the graph set up, end turn is allowed if you stay within the same room from your previous turn or start turn as you may not be able to escape due to rolls.
