from copy import copy, deepcopy
from utils.utils import load_json

class Enchantment:
    def __init__(self, enchantment_id, name, effects, value_multiplier):
        """
        :param enchantment_id: The ID of the enchantment.
        :param name: Human-readable name of the enchantment.
        :param effects: A list of effects with target and level details.
        :param value_multiplier: Multiplier for the value of the card.
        """
        self.enchantment_id = enchantment_id
        self.name = name
        self.effects = deepcopy(effects)  # Each effect has an ID, target, and level
        self.value_multiplier = value_multiplier

    def create_enchanted_card(self, card_prototype):
        """
        Apply this enchantment to a card prototype and return a new enchanted card.
        :param card_prototype: The original card to apply the enchantment to.
        """
        enchanted_card = copy(card_prototype)
        enchanted_card.effects = deepcopy(card_prototype.effects)

        # Merge effects while respecting the target
        for effect in self.effects:
            effect_id = effect["effect_id"]
            target = effect["target"]
            level = effect["level"]

            # Add or merge the effect into the card's effects list
            enchanted_card.effects.append({
                "effect_id": effect_id,
                "target": target,
                "level": level
            })

        # Update the card's name and value
        enchanted_card.name = enchanted_card.enchanted_name.format(self.name)
        enchanted_card.card_id = enchanted_card.name.replace(" ", "_").upper()
        enchanted_card.value = int(card_prototype.value * self.value_multiplier)

        return enchanted_card


class EnchantmentRegistry:
    def __init__(self, effect_registry, enchantments_path):
        """
        :param effect_registry: A registry of all valid effects.
        :param enchantments_path: Path to the JSON file with enchantment definitions.
        """
        self.enchantments = self._register_enchantments(effect_registry, enchantments_path)

    def _create_enchantment(self, enchantment_id, data, effect_registry):
        """
        Create an Enchantment object from JSON data.
        :param enchantment_id: The unique ID of the enchantment.
        :param data: The JSON data for the enchantment.
        :param effect_registry: The effect registry to validate effects.
        """
        name = data["NAME"]
        effects = []

        for effect_data in data["EFFECTS"]:
            effect_id = effect_data["effect_id"]
            level = effect_data["level"]
            target = effect_data["target"]

            if not effect_registry.get_effect(effect_id):
                raise ValueError(f"Effect '{effect_id}' not found in registry.")

            effects.append({"effect_id": effect_id, "level": level, "target": target})

        value_multiplier = data.get("VALUE_MULTIPLIER", 1.0)  # Default multiplier is 1.0
        return Enchantment(enchantment_id, name, effects, value_multiplier)

    def _register_enchantments(self, effect_registry, path):
        """
        Load and register enchantments from JSON.
        """
        enchantments = {}
        data = load_json(path)

        for enchantment_id, enchantment_data in data.items():
            enchantment = self._create_enchantment(enchantment_id, enchantment_data, effect_registry)
            enchantments[enchantment_id] = enchantment

        return enchantments

    def get_enchantment(self, enchantment_id):
        """
        Retrieve an Enchantment by its ID.
        """
        if enchantment_id not in self.enchantments:
            raise KeyError(f"Enchantment ID '{enchantment_id}' not found.")
        return self.enchantments[enchantment_id]
