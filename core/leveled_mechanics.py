"""
This module defines instances of leveled mechanics, which are effects or statuses.
"""
from math import floor
from utils.constants import MIN_EFFECT
from core.effects import Effect
from core.statuses import Status

class LeveledMechanic:
    """
    Represents an effect or status instance along with its level.
    """
    def __init__(self, reference, level):
        """
        Initialize a new LeveledMechanic.
        """
        self.reference = reference
        if isinstance(reference, Effect):
            self.str_id = reference.effect_id
        elif isinstance(reference, Status):
            self.str_id = reference.status_id
        else:
            raise ValueError("Reference must be an Effect or Status instance.")
        self.name = self.reference.name
        self.base_level = level
        self.min_level = MIN_EFFECT if isinstance(self.reference, Effect) else 0
        # self.modifier = 0
        self.num_id = hash(self.str_id)
    
    def __str__(self):
        return f"{self.name} {self.get_level()}"

    def get_level(self, card=None, owner=None, attribute_registry=None) -> int:
        """
        Get the current level of the effect or status.
        """
        if card and owner and attribute_registry:
            return self.resolve_level(card, owner, attribute_registry)
        return self.base_level

    # def change_level_modifier(self, amount):
    #     """
    #     Change the level modifier of the effect or status.
    #     """
    #     self.modifier += amount

    # def reset_level(self):
    #     """
    #     Reset the effect or status to its base level.
    #     """
    #     self.modifier = 0

    def change_level(self, amount):
        """
        Change the base level of the effect or status.
        """
        self.base_level += amount
    
    def resolve_level(self, card, owner, attribute_registry) -> int:
        """
        Resolve the level based on attributes.
        """
        modifier = 0
        # Find the attribute that modifies this effect for this card type, if any
        attribute = attribute_registry.get_attribute_by_context(
            card.card_type, self.str_id
            )
        if attribute is None:
            return self.get_level()
        # Get the level of the attribute and calculate the modifier
        attribute_level = owner.get_attribute_level(attribute)
        base_modifier = attribute_registry.get_modifier(attribute, card.subtype)
        modifier = base_modifier * attribute_level
        # Calculate and return the final level
        return max(floor(self.get_level() * (1 + modifier)), self.min_level)
