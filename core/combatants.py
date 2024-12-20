from gameplay.card_manager import CardManager
from gameplay.status_manager import StatusManager
from utils.constants import StatusNames

class Combatant:
    def __init__(self, name, max_health, max_stamina, max_magicka, starting_deck, card_cache):
        self.name = name
        self.max_health = max_health
        self.max_stamina = max_stamina
        self.max_magicka = max_magicka
        self.card_manager = CardManager(starting_deck, card_cache)
        self.status_manager = StatusManager()
        self.replenish_health()
        self.replenish_stamina()
        self.replenish_magicka()
        
    def replenish_health(self):
        self.health = self.max_health
    
    def replenish_stamina(self):
        self.stamina = self.max_stamina
    
    def replenish_magicka(self):
        self.magicka = self.max_magicka
    
    def gain_resource(self, resource_enum, amount):
        resource = resource_enum.value.attribute_name
        current_value = getattr(self, resource, None)
        if current_value is None:
            raise AttributeError(f"'{resource}' is not a valid resource.")
        
        max_value = getattr(self, resource_enum.value.max_attribute)
        new_value = current_value + amount
        if max_value is not None:
            new_value = min(new_value, max_value)
        setattr(self, resource, new_value)
        
    def take_damage(self, amount, damage_type_enum, status_registry) -> bool:
        # check for weakness or resistance
        amount = self.status_manager.trigger_status_instantly(self, StatusNames.DEFENSE.name, status_registry, default=amount, incoming_damage=amount)
        self.health = max(self.health - amount, 0)
        return self.is_alive()
    
    def is_alive(self) -> bool:
        return self.health > 0
    
    def try_spend_resource(self, resource, amount) -> bool:
        current_value = getattr(self, resource, None)
        if current_value is None:
            raise AttributeError(f"'{resource}' is not a valid resource.")
        
        if current_value < amount:
            return False
        
        setattr(self, resource, current_value - amount)
        return True