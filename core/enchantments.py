from copy import copy
from utils.constants import EnchantmentNames as E
from utils.utils import load_json

class Enchantment:
    def __init__(self, enchantment_id, name, leveled_effects):
        self.enchantment_id = enchantment_id
        self.name = name
        self.leveled_effects = copy(leveled_effects)
    
    def create_enchanted_card(self, card_prototype):
        enchanted_card = copy(card_prototype)
        enchanted_card.effects.update(self.effects)
        enchanted_card.name = enchanted_card.enchanted_name.format(self.name)
        return enchanted_card

class EnchantmentRegistry:
    def __init__(self, effect_registry, enchantments_path):
        self.enchantments = self._register_enchantments(effect_registry, enchantments_path)
    
    def _register_enchantments(self, effect_registry, path) -> dict:
        data = load_json(path)
        
        flame_effect = effect_registry.effects[E.FLAME.name]
        flame_enchantment = Enchantment(E.FLAME.name, E.FLAME.value, flame_effect, data)#flame_effect_level)
        
        enchantments = {
            flame_enchantment.enchantment_id: flame_enchantment
            }
        
        return enchantments