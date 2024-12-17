from enum import Enum

class Resources(Enum):
    HEALTH = "Health"
    STAMINA = "Stamina"
    MAGICKA = "Magicka"
    GOLD = "Gold"

class DamageTypes(Enum):
    PHYSICAL = "Physical"
    FIRE = "Fire"
    FROST = "Frost"
    SHOCK = "Shock"
    POISON = "Poison"
    MAGIC = "Magic"

class EffectNames(Enum):
    DAMAGE = "Damage"
    RESTORE = "Restore"
    PICKPOCKET = "Pickpocket"
    GAIN_DEFENSE = "Gain Defense"
    REMOVE = "Remove"

class StatusNames(Enum):
    DEFENSE = "Defense"
    EVASION = "Evasion"
    POISON = "Poison"

STARTING_HEALTH = 10
STARTING_STAMINA = 3
STARTING_MAGICKA = 3
MAX_NAME_LENGTH = 20

CARD_PATHS = [ 
    "data/cards/weapon_cards.json",
    "data/cards/armor_cards.json",
    "data/cards/spell_cards.json",
    "data/cards/enemy_cards.json" 
    ]
ENEMIES_PATH = "data/enemies.json"
STARTING_DECKS_PATH = "data/starting_decks.json"
QUESTS_PATH = "data/quests.json"
ENCHANTMENTS_PATH = "data/enchantments.json"

SPLASH_MESSAGE = "Welcome to the game!"
PROMPT_NAME = "What is your character’s name? "
ENTER_TOWN_MESSAGE = "Entering Seyda Neen."
VICTORY_MESSAGE = "You won!"
DEFEAT_MESSAGE = "Game over!"
BEAT_GAME_MESSAGE = "You beat the game!"
TEXT_DIVIDER = "------------------------------------------------------------"
DISPLAY_TURN_INFO = "{}\nEnemy {} | Health:{}/{}\n{} Cards in Deck | {} Cards in Discard\n{}\n{} | Health:{}/{} | Stamina:{}/{}\n{} Cards in Deck | {} Cards in Discard\nCards in Hand:"
DISPLAY_CARD = "{}. {} (Cost: {})"
DISPLAY_CARD_EFFECT = "     {} {}"
PROMPT_TURN_OPTIONS = "Enter the number of the Card you want to Play or type PASS to end your Turn: "
NOT_ENOUGH_STAMINA_MESSAGE = "You’re too fatigued to do that!"
CARD_PLAYED_MESSAGE = "{} attacked with {}! {} has {} health left!"
ENEMY_PASSES_MESSAGE = "{} passes their turn."
INPUT_PASS_TURN = "PASS"