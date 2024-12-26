from core.effects import EffectRegistry
from core.statuses import StatusRegistry
from core.enchantments import EnchantmentRegistry

class Registries:
    def __init__(self, statuses_path, enchantments_path):
        self.statuses = StatusRegistry(statuses_path)
        self.effects = EffectRegistry(self.statuses)
        self.enchantments = EnchantmentRegistry(enchantments_path, self.effects)