"""
This module defines instances of leveled mechanics, which are effects or statuses.
"""

class LeveledMechanic:
    """
    Represents an effect or status instance along with its level.
    """
    def __init__(self, reference, level):
        """
        Initialize a new LeveledMechanic.
        """
        self.reference = reference  # This can be an effect or status reference
        self.base_level = level
        self.modifier = 0
    
    def __str__(self):
        return f"{self.reference.name} {self.get_level()}"

    def get_level(self):
        """
        Get the current level of the effect.
        """
        return max(round(self.base_level * (1 + self.modifier)), c.MIN_EFFECT)

    def change_level(self, amount):
        """
        Change the level of the effect.
        """
        self.modifier += amount

    def reset_level(self):
        """
        Reset the effect to its original level.
        """
        self.modifier = 0