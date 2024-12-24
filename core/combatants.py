from gameplay.card_manager import CardManager
from gameplay.status_manager import StatusManager
from utils.constants import StatusNames, Resources, MIN_RESOURCE

class Combatant:
    def __init__(self, name, max_health, max_stamina, max_magicka, starting_deck, card_cache):
        self.name = name
        self.health = Resource(Resources.HEALTH, max_health)
        self.stamina = Resource(Resources.STAMINA, max_stamina)
        self.magicka = Resource(Resources.MAGICKA, max_magicka)
        self.card_manager = CardManager(starting_deck, card_cache)
        self.status_manager = StatusManager()
        
    def take_damage(self, amount, damage_type_enum, status_registry) -> bool:
        # check for weakness or resistance
        amount = self.status_manager.trigger_status_instantly(self, StatusNames.DEFENSE.name, status_registry, default=amount, incoming_damage=amount)
        self.health = max(self.health - amount, 0)
        return self.is_alive()
    
    def is_alive(self) -> bool:
        return self.health.current_value > 0
    
    def reset_for_turn(self):
        self.card_manager.reset_cards_to_draw()
        self.card_manager.reset_cards()
        self.health.reset_max_value()
        self.stamina.reset_max_value()
        self.magicka.reset_max_value()

class Resource:
    def __init__(self, resource_enum, max_value):
        self.resource_enum = resource_enum
        self.max_value = max_value
        self.modified_max_value = max_value
        self.current_value = max_value
    
    def try_spend(self, amount) -> bool:
        if self.current_value < amount:
            return False
        self.current_value = self.current_value - amount
        return True
    
    def reset_max_value(self):
        self.modified_max_value = self.max_value
    
    def get_max_value(self) -> int:
        return self.modified_max_value
    
    def set_max_value(self, new_value):
        new_value = max(new_value, MIN_RESOURCE)
        self.current_value = min(self.current_value, new_value)
        self.modified_max_value = new_value
    
    def replenish(self):
        self.current_value = self.modified_max_value