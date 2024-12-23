from gameplay.card_manager import CardManager
from gameplay.status_manager import StatusManager
from utils.constants import StatusNames, Resources

class Combatant:
    def __init__(self, name, max_health, max_stamina, max_magicka, starting_deck, card_cache):
        self.name = name
        self.stamina = Resource()
        self.card_manager = CardManager(starting_deck, card_cache)
        self.status_manager = StatusManager(Resources.STAMINA)
        self.replenish_health()
        self.replenish_stamina()
        self.replenish_magicka()
        
    def replenish_health(self):
        self.health = self.max_health
    
    def replenish_stamina(self):
        self.stamina = self.max_stamina
    
    def replenish_magicka(self):
        self.magicka = self.max_magicka
    
    def change_resource(self, resource_enum, amount):
        resource = resource_enum.value.attribute_name
        current_value = getattr(self, resource, None)
        if current_value is None:
            raise AttributeError(f"'{resource}' is not a valid resource.")
        
        max_value = getattr(self, resource_enum.value.max_attribute)
        new_value = current_value + amount
        if max_value is not None:
            new_value = min(new_value, max_value)
        new_value = max(new_value, 0)
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
    
    def reset_max_resources(self):
        self.modified_max_stamina = self.max_stamina
        self.modified_max_magicka = self.max_magicka

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