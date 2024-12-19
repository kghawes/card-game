from core.effects import EffectRegistry
from core.statuses import StatusRegistry
from core.enchantments import EnchantmentRegistry

class Registries:
    def __init__(self, effects_path, statuses_path, enchantments_path):
        self.effects = EffectRegistry(effects_path)
        self.statuses = StatusRegistry(statuses_path)
        self.enchantments = EnchantmentRegistry(self.effects, enchantments_path)