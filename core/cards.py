"""
This module defines the Card class, the helper class EffectLevel, as well as
the CardPrototype and CardCache.
"""
from utils.utils import Prototype
from utils.formatter import Formatter
import utils.constants as c
from core.leveled_mechanics import LeveledMechanic

class Card:
    """
    Represents a card in game.
    """
    def __init__(self, name, card_type, cost, value, effects, subtype=None):
        """
        Initialize a new Card.
        """
        self.name = name
        self.card_id = hash(name)
        self.card_type = card_type
        self.cost = cost
        self.cost_modifier = 0
        self.temp_cost_modifier = 0
        self.override_cost = -1
        self.value = value
        self.subtype = subtype
        self.effects = effects
        self.formatter = Formatter()

    def get_card_data(self) -> dict:
        """
        Get a dictionary of the card's data.
        """
        effect_data = self.formatter.format_effect_data(self.effects)

        return {
            "name": self.name,
            "id": self.card_id,
            "type": self.card_type,
            "cost": self.get_cost(),
            "value": self.value,
            "subtype": self.subtype,
            "effects": effect_data
        }

    def get_resource(self) -> str:
        """
        Get the id of the resource corresponding to this card's cost.
        """
        if self.card_type == c.CardTypes.SPELL.name:
            return c.Resources.MAGICKA.name
        return c.Resources.STAMINA.name

    def get_cost(self, enable_override=True) -> int:
        """
        Get the stamina or magicka cost of the card.
        """
        if enable_override and self.override_cost >= c.MIN_COST:
            return self.override_cost
        net_cost = self.cost + self.cost_modifier + self.temp_cost_modifier
        return max(net_cost, c.MIN_COST)

    def change_cost_modifier(self, amount):
        """
        Change the cost of the card.
        """
        self.cost_modifier += amount

    def reset_cost_modifier(self):
        """
        Reset the cost of the card to its base value.
        """
        self.cost_modifier = 0

    def change_temp_cost_modifier(self, amount):
        """
        Add a temporary cost change.
        """
        self.temp_cost_modifier += amount

    def reset_temp_cost_modifier(self):
        """
        Remove temporary cost changes.
        """
        self.temp_cost_modifier = 0

    def reset_override_cost(self):
        """
        Stop using the override cost.
        """
        self.override_cost = -1

    def reset_card(self):
        """
        Reset all modified values on the card.
        """
        for effect in self.effects:
            effect.reset_level()
        self.reset_cost_modifier()
        self.reset_temp_cost_modifier()
        self.reset_override_cost()

    def matches(self, card_property) -> bool:
        """
        Check if a card has a certain type or subtype.
        """
        return card_property in (self.card_type, self.subtype)


class CardPrototype(Card, Prototype):
    """
    This class represents a specific card that may be 'printed' any number of
    times.
    """
    def __init__(
            self, name, card_type, cost, value, effects,
            subtype=c.DEFAULT_SUBTYPE, enchantments=None, enchanted_name=None
            ):
        """
        Initialize a new CardPrototype.
        """
        super().__init__(name, card_type, cost, value, effects, subtype)
        self.enchantments = enchantments
        self.enchanted_name = enchanted_name

    required_fields = ["name", "card_type", "cost", "value", "effects"]

    def clone(self, effect_registry) -> Card:
        """
        Create an instance of this card.
        """
        effects = []
        for effect, level in self.effects.items():
            # Use the effect registry to get the actual effect instance based on the prototype's effect
            effects.append(LeveledMechanic(effect_registry.get_effect(effect), level))
        return Card(
            self.name, self.card_type, self.cost, self.value, effects,
            self.subtype
            )


class CardCache:
    """
    Holds all the card prototype data.
    """
    def __init__(self, filenames, registries):
        """
        Initialize a new CardCache.
        """
        self.card_prototypes = {}
        for filename in filenames:
            self._load_prototypes_from_file(filename, registries)

    def _load_prototypes_from_file(self, filename, registries):
        """
        Load card data from JSON and populate the dictionary.
        """
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
                if effect_level < 0:
                    raise ValueError(
                        f"Invalid effect level for '{effect}' on '{card_id}'."
                        )

            # Add the base card prototype
            self.card_prototypes[card_id] = prototype

            # Generate enchanted versions if specified
            if prototype.enchantments is not None:
                self._generate_enchanted_prototypes(prototype, registries)

    def _generate_enchanted_prototypes(self, prototype, registries):
        """
        Create variants of a card for generic enchantments.
        """
        for enchant_id in prototype.enchantments:
            enchantment = registries.enchantments.get_enchantment(enchant_id)
            enchanted_card = enchantment.create_enchanted_card(prototype)

            if enchanted_card.card_id in self.card_prototypes:
                raise ValueError(f"Duplicate card '{enchanted_card.card_id}'.")

            self.card_prototypes[enchanted_card.card_id] = enchanted_card

    def create_card(self, card_id: str, effect_registry) -> Card:
        """
        Get an instance of a Card based on the prototype id.
        """
        if card_id not in self.card_prototypes:
            raise KeyError(f"Card ID '{card_id}' not found.")
        return self.card_prototypes[card_id].clone(effect_registry)

    def list_cards(self):
        """
        List all card prototype ids in the cache.
        """
        return list(self.card_prototypes.keys())
