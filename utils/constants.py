"""
This module contains constants needed across the codebase.
"""
from enum import Enum

class ClassSpecializations(Enum):
    """
    Player character classes' specializations.
    """
    FIGHTER = "COMBAT"
    THIEF = "STEALTH"
    MAGE = "MAGIC"


class CardTypes(Enum):
    """
    All cards are divided into these types.
    """
    WEAPON = "Weapon"
    ARMOR = "Armor"
    SKILL = "Skill"
    SPELL = "Spell"
    ITEM = "Item"
    CONSUMABLE = "Consumable"


class CardSubtypes(Enum):
    """
    Certain card types have subtypes.
    """
    LONG_BLADE = "Long Blade"
    BLUNT_WEAPON = "Blunt Weapon"
    SHORT_BLADE = "Short Blade"
    MARKSMAN = "Marksman Weapon"
    STAFF = "Staff"
    HEAVY = "Heavy Armor"
    MEDIUM = "Medium Armor"
    LIGHT = "Light Armor"
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
    """
    Combatant stats.
    """
    HEALTH = "Health"
    STAMINA = "Stamina"
    MAGICKA = "Magicka"


class DamageTypes(Enum):
    """
    Damage must come in one of these types.
    """
    PHYSICAL = "Physical"
    FIRE = "Fire"
    FROST = "Frost"
    SHOCK = "Shock"
    POISON = "Poison"


class EffectNames(Enum):
    """
    Effect ids and display names.
    """
    ALL_EFFECTS = "All Effects"
    NO_EFFECT = "No Effect"
    DAMAGE = "Damage"
    RESTORE = "Restore"
    APPLY = "Apply"
    REMOVE = "Remove"
    DRAW = "Draw"
    DISCARD = "Discard"
    JUMP = "Jump"
    DISPEL = "Dispel"


class TargetTypes(Enum):
    """
    The target of a card effect.
    """
    SELF = "on Self"
    TARGET = "on Target"


class StatusNames(Enum):
    """
    Status ids and display names.
    """
    DEFENSE = "Defense"
    REGENERATION = "Regenerate Health"
    POISON = "Poison"
    PARALYZE = "Paralyze"
    SILENCE = "Silence"
    BLIND = "Blind"
    FRENZY = "Frenzy"
    CALM = "Calm"
    EVASION = "Evasion"
    HIDDEN = "Hidden"
    BURDEN = "Burden"
    FEATHER = "Feather"
    DISEASE = "Common Disease"
    BLIGHT = "Blight Disease"
    REFLECT = "Reflect"
    SPELL_ABSORPTION = "Spell Absorption"
    ALCHEMIST = "Alchemist"
    ENCHANTER = "Enchanter"
    LEVITATE = "Levitate"
    SLOWFALLING = "Slowfalling"
    WATER_WALKING = "Water Walking"
    WATER_BREATHING = "Water Breathing"
    SWIFT_SWIM = "Swift Swim"
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


class MerchantProbabilities(Enum):
    """
    The probability for a card of the given type to appear in the shop.
    """
    WEAPON = 0.23
    ARMOR = 0.19
    SKILL = 0.18
    SPELL = 0.23
    ITEM = 0.13
    CONSUMABLE = 0.04


# Minimum values
MIN_RESOURCE = 0
MIN_EFFECT = 1
MIN_COST = 0

# Status parameters
BASE_EVASION_PROBABILITY = 0.1
BASE_CRIT_PROBABILITY = 0.1
CRIT_MULTIPLIER = 2
SCALE_FACTOR = 0.2

# Game parameters
STARTING_HEALTH = 10
STARTING_STAMINA = 4
STARTING_MAGICKA = 0
MAX_NAME_LENGTH = 20
HAND_SIZE = 6
MIN_HAND_SIZE = 2
MAX_HAND_SIZE = 12
MIN_DECK_SIZE = 10
MAX_DECK_SIZE = 50
MAX_CARD_FREQUENCY = 5
NORMAL_CARD_REWARD = 1
BOSS_CARD_REWARD = 2
BOSS_ID = "BOSS"
DEFAULT_SUBTYPE = "MISC"
ALLOWED_TYPES = {
    "ALL": [
        "ALTERATION",
        "CONJURATION",
        "DESTRUCTION",
        "ILLUSION",
        "MYSTICISM",
        "RESTORATION",
        "SCROLL",
        "POTION",
        DEFAULT_SUBTYPE
        ],
    "FIGHTER": [
        "LONG_BLADE",
        "BLUNT_WEAPON",
        "HEAVY",
        "MEDIUM",
        "COMBAT"
        ],
    "THIEF": [
        "SHORT_BLADE",
        "MARKSMAN",
        "LIGHT",
        "MEDIUM",
        "STEALTH"
        ],
    "MAGE": [
        "STAFF",
        "MAGIC"
        ]
    }
class Attributes(Enum):
    """
    Character attributes.
    """
    STRENGTH = "Strength"
    ENDURANCE = "Endurance"
    AGILITY = "Agility"
    SPEED = "Speed"
    INTELLIGENCE = "Intelligence"
    WILLPOWER = "Willpower"
    PERSONALITY = "Personality"
    LUCK = "Luck"

# Paths to JSON files
CARD_PATHS = [
    "data/cards/weapons.json",
    "data/cards/armors.json",
    "data/cards/alteration_spells.json",
    "data/cards/destruction_spells.json",
    "data/cards/illusion_spells.json",
    "data/cards/mysticism_spells.json",
    "data/cards/restoration_spells.json",
    "data/cards/combat_skills.json",
    "data/cards/stealth_skills.json",
    "data/cards/magic_skills.json",
    "data/cards/potion_consumables.json",
    "data/cards/scroll_consumables.json",
    "data/cards/items.json",
    "data/cards/enemy_weapons.json",
    "data/cards/enemy_armors.json",
    "data/cards/enemy_spells.json",
    "data/cards/enemy_skills.json"
    ]
ENEMIES_PATHS = [
    "data/enemies/beasts.json",
    "data/enemies/daedra.json",
    "data/enemies/npcs.json",
    "data/enemies/undead.json",
    "data/enemies/dagoth.json",
    "data/enemies/constructs.json",
    "data/enemies/goblins.json"
    ]
STARTING_DECKS_PATH = "data/starting_decks.json"
QUESTS_PATH = "data/quests.json"
ENCHANTMENTS_PATH = "data/enchantments.json"
STATUSES_PATH = "data/statuses.json"
EFFECTS_PATH = "data/effects.json"
CARD_REWARDS_PATH = "data/card_rewards.json"
ENEMY_GROUPS_PATH = "data/enemy_groups.json"

# Experience
EXP_TO_LEVEL = [
    0,
    0,
    30,
    46,
    70,
    99,
    135,
    177,
    225,
    280,
    340,
    407,
    479,
    557,
    642,
    733,
    830,
    933,
    1042,
    1156,
    1277,
    1404,
    1537,
    1676,
    1821,
    1971,
    2128,
    2291,
    2460,
    2635,
    2816,
    3003
]
