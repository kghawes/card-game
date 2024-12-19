from enum import Enum

class ResourceData:
    def __init__(self, name):
        self.attribute_name = name.lower()
        self.display = name.capitalize()
        self.max_attribute = f"max_{name.lower()}"

class Resources(Enum):
    HEALTH = ResourceData("health")
    STAMINA = ResourceData("stamina")
    MAGICKA = ResourceData("magicka")
    GOLD = ResourceData("gold")

class DamageTypes(Enum):
    PHYSICAL = "Physical"
    FIRE = "Fire"
    FROST = "Frost"
    SHOCK = "Shock"
    POISON = "Poison"
    MAGIC = "Magic"

class EffectNames(Enum):
    NO_EFFECT = "No Effect"
    DAMAGE = "Damage"
    RESTORE = "Restore"
    APPLY_STATUS = "+"
    REMOVE_STATUS = "–"
    FORTIFY_ATTRIBUTE = "Fortify"
    DAMAGE_ATTRIBUTE = "Damage"
    DRAIN_ATTRIBUTE = "Drain"
    DRAW = "Draw"
    DISCARD = "Discard"
    JUMP = "Jump"
    SCRY = "Scry"
    PICKPOCKET = "Pickpocket"
    DISPEL = "Dispel"
    CONJURE_CARD = "Conjure"
    
class TargetTypes(Enum):
    SELF = "on Self"
    TARGET = "on Target"

class StatusNames(Enum):
    DEFENSE = "Defense"
    REGENERATION = "Regenerate Health"
    POISON = "Poison"
    PARALYSIS = "Paralysis"
    SILENCE = "Silence"
    BLIND = "Blind"
    FRENZY = "Frenzy"
    CALM = "Calm"
    EVASION = "Evasion"
    HIDDEN = "Hidden"
    BURDEN = "Burden"
    FEATHER = "Feather"
    WATERWALKING = "Waterwalking"
    WATERBREATHING = "Waterbreathing"
    SWIFT_SWIM = "Swift Swim"
    WEAKNESS = "Weakness to"
    RESISTANCE = "Resist"
    DISEASE = "Common Disease"
    BLIGHT = "Blight Disease"
    REFLECT = "Reflect"
    SPELL_ABSORPTION = "Spell Absorption"
    ALCHEMIST = "Alchemist"
    FORTIFY_STRENGTH = "Fortify Strength"
    DAMAGE_STRENGTH = "Damage Strength"
    FORTIFY_AGILITY = "Fortify Agility"
    DAMAGE_AGILITY = "Damage Agility"
    FORTIFY_INTELLIGENCE = "Fortify Intelligence"
    DAMAGE_INTELLIGENCE = "Damage Intelligence"
    FORTIFY_WILLPOWER = "Fortify Willpower"
    DAMAGE_WILLPOWER = "Damage Willpower"
    FORTIFY_ENDURANCE = "Fortify Endurance"
    DAMAGE_ENDURANCE = "Damage Endurance"
    FORTIFY_SPEED = "Fortify Speed"
    DAMAGE_SPEED = "Damage Speed"
    FORTIFY_LUCK = "Fortify Luck"
    DAMAGE_LUCK = "Damage Luck"

class StatusParameters(Enum):
    BASE_EVASION_PROBABILITY = 0.1

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
EFFECTS_PATH = "data/effects.json"
STATUSES_PATH = "data/statuses.json"

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