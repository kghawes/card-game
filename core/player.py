import utils.constants as c
from utils.utils import load_json
from core.combatants import Combatant

class Player(Combatant):
    def __init__(self, card_cache, status_registry):
        deck_list = load_json(c.STARTING_DECKS_PATH).get("STARTING_DECK")
        super().__init__(
            "", c.STARTING_HEALTH, c.STARTING_STAMINA, c.STARTING_MAGICKA, 
            deck_list, card_cache, status_registry
            )
        self.gold = 0
        self.level = 1
        
    def gain_gold(self, amount):
        self.gold += amount
        
    def try_spend_gold(self, amount):
        return self.try_spend_resource(c.Resources.GOLD.value, amount)
        
        