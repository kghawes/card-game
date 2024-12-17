from copy import copy, deepcopy
from utils.utils import load_json

class Enchantment:
    def __init__(self, enchantment_id, name, leveled_effects, value_multiplier):
        self.enchantment_id = enchantment_id
        self.name = name
        self.leveled_effects = copy(leveled_effects)
        self.value_multiplier = value_multiplier

    def create_enchanted_card(self, card_prototype):
        enchanted_card = copy(card_prototype)
        enchanted_card.effects = deepcopy(card_prototype.effects)

        # Merge effects
        for effect_id, level in self.leveled_effects.items():
            if effect_id in enchanted_card.effects:
                enchanted_card.effects[effect_id] += level
            else:
                enchanted_card.effects[effect_id] = level

        enchanted_card.name = enchanted_card.enchanted_name.format(self.name)
        enchanted_card.card_id = enchanted_card.name.replace(" ", "_").upper()
        enchanted_card.value = int(card_prototype.value * self.value_multiplier)

        return enchanted_card


class EnchantmentRegistry:
    def __init__(self, effect_registry, enchantments_path):
        self.enchantments = self._register_enchantments(effect_registry, enchantments_path)

    def _create_enchantment(self, enchantment_id, data, effect_registry):
        name = data["NAME"]
        effects = {}
        for effect_id, level in data["EFFECTS"].items():
            if not effect_registry.get_effect(effect_id):
                raise ValueError(f"Effect '{effect_id}' not found in registry.")
            effects[effect_id] = level

        value_multiplier = data.get("VALUE_MULTIPLIER", 1.0)  # Default multiplier is 1.0
        return Enchantment(enchantment_id, name, effects, value_multiplier)

    def _register_enchantments(self, effect_registry, path):
        enchantments = {}
        data = load_json(path)

        for enchantment_id, enchantment_data in data.items():
            enchantment = self._create_enchantment(enchantment_id, enchantment_data, effect_registry)
            enchantments[enchantment_id] = enchantment

        return enchantments

    def get_enchantment(self, enchantment_id):
        if enchantment_id not in self.enchantments:
            raise KeyError(f"Enchantment ID '{enchantment_id}' not found.")
        return self.enchantments[enchantment_id]
