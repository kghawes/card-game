from utils.utils import Prototype
from utils.constants import CardTypes, CardSubtypes, MIN_EFFECT

class Card:
    def __init__(self, name, card_type, cost, value, effects, subtype=None):
        self.name = name
        self.card_type = card_type
        self.cost = cost
        self.cost_modifier = 1
        self.value = value
        self.subtype = subtype
        self.effects = {}
        self.net_modifiers = {}  # Tracks accumulated modifiers for effects

        for effect, level in effects.items():
            if type(level) is EffectLevel:
                level = level.base_level
            self.effects[effect] = EffectLevel(level)

    def get_cost(self) -> int:
        return self.cost * self.cost_modifier

    def change_cost_modifier(self, amount):
        self.cost_modifier += amount

    def reset_cost_modifier(self):
        self.cost_modifier = 1

    def reset_card(self):
        for level in self.effects.values():
            level.reset_modifier()
        self.reset_cost_modifier()
        self.net_modifiers.clear()  # Clear all cached modifiers

    def matches(self, card_property) -> bool:
        if card_property in CardTypes:
            return self.card_type == card_property.name
        elif card_property in CardSubtypes:
            return self.subtype == card_property.name
        else:
            return False

    def apply_modifier(self, effect, contribution):
        """Apply the accumulated contribution to the net modifier cache."""
        self.net_modifiers[effect] = self.net_modifiers.get(effect, 0) + contribution
        self.recalculate_effect(effect)

    def recalculate_effect(self, effect):
        """Recalculate the effect level based on accumulated modifiers."""
        if effect in self.effects:
            modifier = 1 + self.net_modifiers.get(effect, 0)
            self.effects[effect].set_modifier(modifier)


class EffectLevel():
    def __init__(self, base_level):
        self.base_level = base_level
        self.modifier = 1

    def get_level(self):
        return max(self.base_level * self.modifier, MIN_EFFECT)

    def set_modifier(self, modifier):
        self.modifier = modifier

    def change_modifier(self, amount):
        self.modifier = self.modifier + amount

    def reset_modifier(self):
        self.modifier = 1


class CardPrototype(Card, Prototype):
    def __init__(self, name, card_type, cost, value, effects, enchantments = None, enchanted_name = None):
        super().__init__(name, card_type, cost, value, effects)
        self.enchantments = enchantments
        self.enchanted_name = enchanted_name

    required_fields = ["name", "card_type", "cost", "value", "effects"]

    def clone(self):
        return Card(self.name, self.card_type, self.cost, self.value, self.effects)


class CardCache:
    def __init__(self, filenames, registries):
        self.card_prototypes = {}
        for filename in filenames:
            self._load_prototypes_from_file(filename, registries)

    def _load_prototypes_from_file(self, filename, registries):
        raw_prototypes = CardPrototype.load_prototypes(
            filename=filename,
            required_fields=CardPrototype.required_fields,
            prototype_class=CardPrototype
        )

        for card_id, prototype in raw_prototypes.items():
            if card_id in self.card_prototypes:
                raise ValueError(f"Duplicate card ID '{card_id}' found in file '{filename}'.")

            # Add the base card prototype
            self.card_prototypes[card_id] = prototype

            # Generate enchanted versions if specified
            if prototype.enchantments is not None:
                self._generate_enchanted_prototypes(card_id, prototype, registries)

    def _generate_enchanted_prototypes(self, base_card_id, prototype, registries):
        for enchantment_id in prototype.enchantments:
            enchantment = registries.enchantments.get_enchantment(enchantment_id)
            enchanted_card = enchantment.create_enchanted_card(prototype, registries.effects)

            if enchanted_card.card_id in self.card_prototypes:
                raise ValueError(f"Duplicate card ID '{enchanted_card.card_id}' generated for '{base_card_id}'.")

            self.card_prototypes[enchanted_card.card_id] = enchanted_card

    def create_card(self, card_id: str) -> Card:
        if card_id not in self.card_prototypes:
            raise KeyError(f"Card ID '{card_id}' not found.")
        return self.card_prototypes[card_id].clone()

    def list_cards(self):
        return list(self.card_prototypes.keys())
