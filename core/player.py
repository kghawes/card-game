import utils.constants as constants
from combatants import Combatant

class Player(Combatant):
    def __init__(self):
        super().__init__("", constants.STARTING_HEALTH, constants.STARTING_STAMINA, constants.)
        self.gold = 0
        
    def gain_gold(self, amount):
        self.gold += amount
        
    def try_spend_gold(self, amount):
        return self.try_spend_resource(constants.Resources.GOLD.value, amount)