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
    def __init__(self, card_cache, status_registry):
        """
        Initialize a new Player.
        """
        deck_list = load_json(c.STARTING_DECKS_PATH).get("STARTING_DECK")
        super().__init__(
            "", c.STARTING_HEALTH, c.STARTING_STAMINA, c.STARTING_MAGICKA, 
            deck_list, card_cache, status_registry
            )
        self.gold = 0
        self.level = 1

    def gain_gold(self, amount):
        """
        Increase gold by given amount.
        """
        self.gold += amount

    def try_spend_gold(self, amount) -> bool:
        """
        Reduce gold by the given amount or return false if there isn't enough.
        """
        pass
