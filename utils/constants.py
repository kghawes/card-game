"""
This module contains constants needed across the codebase.
"""
from enum import Enum

class CardTypes(Enum):
    """All cards are divided into these types."""
    WEAPON = "Weapon"
    ARMOR = "Armor"
    SKILL = "Skill"
    SPELL = "Spell"
    ITEM = "Item"
    CONSUMABLE = "Consumable"

class CardSubtypes(Enum):
    """Certain card types have subtypes."""
    LONG_BLADE = "Long Blade"
    BLUNT_WEAPON = "Blunt Weapon"
    SHORT_BLADE = "Short Blade"
    MARKSMAN = "Marksman Weapon"
    STAFF = "Staff"
    HEAVY_ARMOR = "Heavy Armor"
    MEDIUM_ARMOR = "Medium Armor"
    LIGHT_ARMOR = "Light Armor"
    COMBAT = "Combat"
    STEALTH = "Stealth"
    MAGIC = "Magic"
    ALTERATION = "Alteration"
    CONJURATION = "Conjuration"
    DESTRUCTION = "Destruction"
    ILLUSION = "Illusion"
    MYSTICISM = "Mysticism"
    RESTORATION = "Restoration"
    SCROLL = "Scroll"
    POTION = "Potion"

class Resources(Enum):
    """Combatant stats."""
    HEALTH = "health"
    STAMINA = "stamina"
    MAGICKA = "magicka"

# Minimum values
MIN_RESOURCE = 0
MIN_EFFECT = 1

class DamageTypes(Enum):
    """Damage must come in one of these types."""
    PHYSICAL = "Physical"
    FIRE = "Fire"
    FROST = "Frost"
    SHOCK = "Shock"
    POISON = "Poison"
    MAGIC = "Magic"

# Damage groups
ELEMENTAL_DAMAGE_TYPES = [
    DamageTypes.FIRE,
    DamageTypes.FROST,
    DamageTypes.SHOCK
    ]

class EffectNames(Enum):
    """Effect ids and display names."""
    NO_EFFECT = "No Effect"
    DAMAGE = "Damage"
    RESTORE = "Restore"
    DRAIN = "Drain"
    APPLY = "Apply"
    REMOVE = "Remove"
    DRAW = "Draw"
    DISCARD = "Discard"
    JUMP = "Jump"
    SCRY = "Scry"
    PICKPOCKET = "Pickpocket"
    DISPEL = "Dispel"
    CONJURE_CARD = "Conjure"

class TargetTypes(Enum):
    """The target of a card effect."""
    SELF = "on Self"
    TARGET = "on Target"

class StatusNames(Enum):
    """Status ids and display names."""
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
    DISEASE = "Common Disease"
    BLIGHT = "Blight Disease"
    REFLECT = "Reflect"
    SPELL_ABSORPTION = "Spell Absorption"
    ALCHEMIST = "Alchemist"
    ENCHANTER = "Enchanter"
    WEAKNESS_PHYSICAL = "Weakness to Physical Damage"
    WEAKNESS_FIRE = "Weakness to Fire Damage"
    WEAKNESS_FROST = "Weakness to Frost Damage"
    WEAKNESS_SHOCK = "Weakness to Shock Damage"
    WEAKNESS_POISON = "Weakness to Poison Damage"
    RESISTANCE_PHYSICAL = "Resist Physical Damage"
    RESISTANCE_FIRE = "Resist Fire Damage"
    RESISTANCE_FROST = "Resist Frost Damage"
    RESISTANCE_SHOCK = "Resist Shock Damage"
    RESISTANCE_POISON = "Resist Poison Damage"
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
    FORTIFY_LONG_BLADE = "Fortify Long Blade"
    FORTIFY_BLUNT_WEAPON = "Fortify Blunt Weapon"
    FORTIFY_SHORT_BLADE = "Fortify Short Blade"
    FORTIFY_MARKSMAN = "Fortify Marksmanship"
    FORTIFY_STAFF = "Fortify Staff"
    FORTIFY_LIGHT_ARMOR = "Fortify Light Armor"
    FORTIFY_MEDIUM_ARMOR = "Fortify Medium Armor"
    FORTIFY_HEAVY_ARMOR = "Fortify Heavy Armor"
    FORTIFY_ALTERATION = "Fortify Alteration"
    FORTIFY_CONJURATION = "Fortify Conjuration"
    FORTIFY_DESTRUCTION = "Fortify Destruction"
    FORTIFY_ILLUSION = "Fortify Illusion"
    FORTIFY_MYSTICISM = "Fortify Mysticism"
    FORTIFY_RESTORATION = "Fortify Restoration"

# Status parameters
BASE_EVASION_PROBABILITY = 0.1
SCALE_FACTOR = 0.2

# Game parameters
STARTING_HEALTH = 10
STARTING_STAMINA = 3
STARTING_MAGICKA = 3
MAX_NAME_LENGTH = 20
HAND_SIZE = 6
MIN_HAND_SIZE = 2
MAX_HAND_SIZE = 10

# Paths to JSON files
CARD_PATHS = [
    "data/cards/weapon_cards.json",
    "data/cards/armor_cards.json",
    "data/cards/spell_cards.json",
    "data/cards/skill_cards.json",
    "data/cards/enemy_cards.json" 
    ]
ENEMIES_PATH = "data/enemies.json"
STARTING_DECKS_PATH = "data/starting_decks.json"
QUESTS_PATH = "data/quests.json"
ENCHANTMENTS_PATH = "data/enchantments.json"
EFFECTS_PATH = "data/effects.json"
STATUSES_PATH = "data/statuses.json"

# Text for UI
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
CARD_PLAYED_MESSAGE = "{} played {}! {} has {} health left!"
ENEMY_PASSES_MESSAGE = "{} passes their turn."
INPUT_PASS_TURN = "PASS"
