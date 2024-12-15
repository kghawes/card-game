from utils.constants import Resources
from gameplay.card_manager import CardManager
from gameplay.status_manager import StatusManager

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
    
    def gain_health(self, amount):
        self.health = min(self.max_health, self.health + amount)
        
    def gain_stamina(self, amount):
        self.stamina = min(self.max_stamina, self.stamina + amount)
        
    def gain_magicka(self, amount):
        self.magicka = min(self.max_magicka, self.magicka + amount)
        
    def take_damage(self, amount, damage_type) -> bool:
        # check for weakness or resistance
        self.health = max(self.health - amount, 0)
        return self.is_alive()
    
    def is_alive(self) -> bool:
        return self.health > 0
    
    def try_spend_resource(self, resource, amount) -> bool:
        resource = resource.lower()
        current_value = getattr(self, resource, None)
        if current_value is None:
            raise AttributeError(f"'{resource}' is not a valid resource.")
        
        if current_value < amount:
            return False
        
        setattr(self, resource, current_value - amount)
        return True

    def try_spend_stamina(self, amount) -> bool:
        x = Resources.STAMINA.value
        return self.try_spend_resource(x, amount)
    
    def try_spend_magicka(self, amount) -> bool:
        return self.try_spend_resource(Resources.MAGICKA.value, amount)