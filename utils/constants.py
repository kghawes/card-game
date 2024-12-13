from enum import Enum

class Resources(Enum):
    STAMINA = "stamina"
    GOLD = "gold"

STARTING_HEALTH = 10
STARTING_STAMINA = 3

CARDS_PATH = "data/cards.json"
ENEMIES_PATH = "data/enemies.json"
STARTING_DECKS_PATH = "data/starting_decks.json"