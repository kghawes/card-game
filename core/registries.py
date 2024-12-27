from core.effects import EffectRegistry
from core.statuses import StatusRegistry
from core.enchantments import EnchantmentRegistry
from gameplay.quests import QuestRegistry

class Registries:
    def __init__(self, statuses_path, enchantments_path):
        self.statuses = StatusRegistry(statuses_path)
        self.effects = EffectRegistry(self.statuses)
        self.enchantments = EnchantmentRegistry(
            enchantments_path, self.effects
            )
        self.quests = None
    
    def register_quests(self, quests_path, enemy_cache, card_cache):
        self.quests = QuestRegistry(
            quests_path, enemy_cache, card_cache, self.statuses
            )