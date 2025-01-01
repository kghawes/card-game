"""
This module defines the Card class, the helper class EffectLevel, as
well as the CardPrototype and CardCache.
"""
from utils.utils import Prototype
from utils.constants import MIN_EFFECT

class Card:
    """Represents a card in game."""
    def __init__(self, name, card_type, cost, value, effects, subtype=None):
        """Initialize a new Card."""
        self.name = name
        self.card_type = card_type
        self.cost = cost
        self.cost_modifier = 1
        self.value = value
        self.subtype = subtype
        self.effects = {}

        for effect, level in effects.items():
            if isinstance(level, EffectLevel):
                level = level.base_level
            self.effects[effect] = EffectLevel(level)

    def get_cost(self) -> int:
        """Get the stamina or magicka cost of the card."""
        return self.cost * self.cost_modifier

    def change_cost_modifier(self, amount):
        """Change the cost of the card."""
        self.cost_modifier += amount

    def reset_cost_modifier(self):
        """Reset the cost of the card to its base value."""
        self.cost_modifier = 1

    def reset_card(self):
        """Reset all modified values on the card."""
        for level in self.effects.values():
            level.reset_level()
        self.reset_cost_modifier()

    def matches(self, card_property) -> bool:
        """Check if a card has a certain type or subtype."""
        return self.card_type == card_property or self.subtype == card_property


class EffectLevel():
    """This class represents the power level of an Effect on the card."""
    def __init__(self, base_level):
        """Initialize a new EffectLevel."""
        self.base_level = base_level
        self.modifier = 0

    def get_level(self):
        """Get the current level of the effect."""
        return max(self.base_level * (1 + self.modifier), MIN_EFFECT)

    def change_level(self, amount):
        """Change the level of the effect."""
        self.modifier += amount

    def reset_level(self):
        """Reset the effect to its original level."""
        self.modifier = 0


class CardPrototype(Card, Prototype):
    """This class represents a specific card that may be 'printed' any
    number of times."""
    def __init__(
            self, name, card_type, cost, value, effects, subtype=None,
            enchantments=None, enchanted_name=None
            ):
        """Initialize a new CardPrototype."""
        super().__init__(name, card_type, cost, value, effects, subtype)
        self.enchantments = enchantments
        self.enchanted_name = enchanted_name

    required_fields = ["name", "card_type", "cost", "value", "effects"]

    def clone(self):
        """Create an instance of this card."""
        return Card(
            self.name, self.card_type, self.cost, self.value, self.effects
            )


class CardCache:
    """Holds all the card prototype data."""
    def __init__(self, filenames, registries):
        """Initialize a new CardCache."""
        self.card_prototypes = {}
        for filename in filenames:
            self._load_prototypes_from_file(filename, registries)

    def _load_prototypes_from_file(self, filename, registries):
        """Load card data from JSON and populate the dictionary."""
        raw_prototypes = CardPrototype.load_prototypes(
            filename=filename,
            required_fields=CardPrototype.required_fields,
            prototype_class=CardPrototype
        )

        for card_id, prototype in raw_prototypes.items():
            if card_id in self.card_prototypes:
                raise ValueError(
                    f"Duplicate card '{card_id}' found in file '{filename}'."
                    )
            for effect, effect_level in prototype.effects.items():
                if effect_level.base_level < 0:
                    raise ValueError(
                        f"Invalid effect level for '{effect}' on '{card_id}'."
                        )

            # Add the base card prototype
            self.card_prototypes[card_id] = prototype

            # Generate enchanted versions if specified
            if prototype.enchantments is not None:
                self._generate_enchanted_prototypes(prototype, registries)

    def _generate_enchanted_prototypes(self, prototype, registries):
        """Create variants of a card for generic enchantments."""
        for enchant_id in prototype.enchantments:
            enchantment = registries.enchantments.get_enchantment(enchant_id)
            enchanted_card = enchantment.create_enchanted_card(
                prototype, registries.effects
                )

            if enchanted_card.card_id in self.card_prototypes:
                raise ValueError(f"Duplicate card '{enchanted_card.card_id}'.")

            self.card_prototypes[enchanted_card.card_id] = enchanted_card

    def create_card(self, card_id: str) -> Card:
        """Get an instance of a Card based on the prototype id."""
        if card_id not in self.card_prototypes:
            raise KeyError(f"Card ID '{card_id}' not found.")
        return self.card_prototypes[card_id].clone()

    def list_cards(self):
        """List all card prototype ids in the cache."""
        return list(self.card_prototypes.keys())
