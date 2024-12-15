import utils.constants as constants
from utils.utils import load_json
from core.combatants import Combatant

class Player(Combatant):
    def __init__(self, card_cache):
        deck_list = load_json(constants.STARTING_DECKS_PATH).get("STARTING_DECK")
        super().__init__("", constants.STARTING_HEALTH, constants.STARTING_STAMINA, constants.STARTING_MAGICKA, deck_list, card_cache)
        self.gold = 0
        
    def gain_gold(self, amount):
        self.gold += amount
        
    def try_spend_gold(self, amount):
        return self.try_spend_resource(constants.Resources.GOLD.value, amount)
        
        