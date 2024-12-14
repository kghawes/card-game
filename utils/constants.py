from enum import Enum

class Resources(Enum):
    STAMINA = "stamina"
    GOLD = "gold"

STARTING_HEALTH = 10
STARTING_STAMINA = 3
MAX_NAME_LENGTH = 20

CARDS_PATH = "data/cards.json"
ENEMIES_PATH = "data/enemies.json"
STARTING_DECKS_PATH = "data/starting_decks.json"

SPLASH_MESSAGE = "Welcome to the game!"
PROMPT_NAME = "What is your character’s name? "
VICTORY_MESSAGE = "You beat the game!"
DEFEAT_MESSAGE = "Game over!"
TEXT_DIVIDER = "------------------------------------------------------------"
DISPLAY_TURN_INFO = "{}\nEnemy {} | Health:{}/{}\n{} Cards in Deck | {} Cards in Discard\n{}\n{} | Health:{}/{} | Stamina:{}/{}\n{} Cards in Deck | {} Cards in Discard\nCards in Hand:"
DISPLAY_CARD = "{}. {} (Cost: {})\n     Deal {} Damage."
PROMPT_TURN_OPTIONS = "Enter the number of the Card you want to Play or type PASS to end your Turn: "
NOT_ENOUGH_STAMINA_MESSAGE = "You’re too fatigued to do that!"
CARD_PLAYED_MESSAGE = "{} attacked with {}! {} has {} health left!"
ENEMY_PASSES_MESSAGE = "{} passes their turn."
INPUT_PASS_TURN = "PASS"