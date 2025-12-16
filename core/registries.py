"""
This module defines the Registries class, containing lookup dictionaries for
statuses, effects, enchantments, and quests.
"""
from core.effects import EffectRegistry
from core.statuses import StatusRegistry
from core.enchantments import EnchantmentRegistry
from core.attributes import AttributeRegistry
from gameplay.quests import QuestRegistry

class Registries:
    """
    Wraps StatusRegistry, EffectRegistry, EnchantmentRegistry, and
    QuestRegistry since these are frequently used together.
    """
    def __init__(self, effects_path, statuses_path, enchantments_path, \
                 attributes_path, event_manager):
        """
        Initialize a new Registries.
        """
        self.statuses = StatusRegistry(statuses_path, event_manager)
        self.effects = EffectRegistry(effects_path, self.statuses)
        self.enchantments = EnchantmentRegistry(
            enchantments_path, self.effects
            )
        self.attributes = AttributeRegistry(attributes_path)
        self.quests = None

    def register_quests(
            self, quests_path, enemy_groups_path, enemy_cache, card_cache,
            card_rewards
            ):
        """
        Create the quest registry.
        """
        self.quests = QuestRegistry(
            quests_path, enemy_groups_path, enemy_cache, card_cache,
            self, card_rewards
            )
