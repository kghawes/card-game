"""
This module defines instances of leveled mechanics, which are effects or statuses.
"""
import utils.constants as c
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
        self.min_level = c.MIN_EFFECT if isinstance(self.reference, Effect) else 0
        self.modifier = 0
        self.num_id = hash(self.str_id)
    
    def __str__(self):
        return f"{self.reference.name} {self.get_level()}"

    def get_level(self):
        """
        Get the current level of the effect or status.
        """
        return max(round(self.base_level * (1 + self.modifier)), self.min_level)

    def change_level_modifier(self, amount):
        """
        Change the level modifier of the effect or status.
        """
        self.modifier += amount

    def reset_level(self):
        """
        Reset the effect or status to its base level.
        """
        self.modifier = 0

    def change_level(self, amount):
        """
        Change the base level of the effect or status.
        """
        self.base_level += amount
