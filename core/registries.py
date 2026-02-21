"""
This module defines the Registries class, containing lookup dictionaries for
statuses, effects, enchantments, cards, enemies, and quests.
"""
from core.effects import EffectRegistry
from core.statuses import StatusRegistry
from core.enchantments import EnchantmentRegistry
from core.attributes import AttributeRegistry
from core.cards import CardRegistry
from core.enemies import EnemyRegistry
from gameplay.quests import QuestRegistry
from utils.constants import JSON_PATHS as paths

class Registries:
    """
    This class holds all the registries for the game.
    """
    def __init__(self, event_manager):
        """
        Initialize the Registries.
        """
        self.attributes = AttributeRegistry(paths['attributes'])
        self.statuses = StatusRegistry(paths['statuses'], event_manager)
        self.effects = EffectRegistry(paths['effects'], self.statuses)
        self.enchantments = EnchantmentRegistry(
            paths['enchantments'], self.effects
            )
        self.cards = CardRegistry(paths['cards'], self.enchantments)
        self.enemies = EnemyRegistry(paths['enemies'], event_manager)
        self.quests = QuestRegistry(
            paths['quests'], paths['enemy_groups'], self
            )
