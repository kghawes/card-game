"""
This module defines the Player class.
"""
import utils.constants as c
from utils.utils import load_json
from core.combatants import Combatant

class Player(Combatant):
    """
    This class represents the player character.
    """
    def __init__(self, card_cache, status_registry, character_class):
        """
        Initialize a new Player.
        """
        deck_list = load_json(c.STARTING_DECKS_PATH).get("STARTING_DECK")
        super().__init__(
            "", c.STARTING_HEALTH, c.STARTING_STAMINA, c.STARTING_MAGICKA, 
            deck_list, card_cache, status_registry
            )
        self.character_class = character_class
        self.gold = 0
        self.level = 1
        self.exp = 0

    def gain_gold(self, amount):
        """
        Increase gold by given amount.
        """
        self.gold += amount

    def try_spend_gold(self, amount) -> bool:
        """
        Reduce gold by the given amount or return false if there isn't enough.
        """
        if amount > self.gold:
            return False
        self.gold -= amount
        return True

    def gain_exp(self, amount, text_interface):
        """
        Increase experience by given amount and level up if necessary.
        """
        self.exp += amount
        if self.exp >= c.EXP_TO_LEVEL[self.level + 1]:
            self.level_up(text_interface)

    def level_up(self, text_interface):
        """
        Increase level and reset experience.
        """
        self.level += 1
        self.exp -= c.EXP_TO_LEVEL[self.level]
        resource_to_increase = text_interface.level_up_prompt(self)
        self.resources[resource_to_increase].max_value += 1
        new_max = self.resources[resource_to_increase].max_value
        text_interface.send_message(
            f"MAX {resource_to_increase} is now {new_max}!"
            )
