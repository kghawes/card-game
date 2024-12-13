from constants import Resources
import CardManager

class Combatant:
    def __init__(self, name, max_health, max_stamina, starting_deck):
        self.name = name
        self.max_health = max_health
        self.max_stamina = max_stamina
        self.card_manager = CardManager(starting_deck.clone())
        self.replenish_health()
        self.replenish_stamina()
        
    def replenish_health(self):
        self.health = self.max_health
    
    def replenish_stamina(self):
        self.stamina = self.max_stamina
        
    def take_damage(self, amount) -> bool:
        self.health = max(self.health - amount, 0)
        return self.is_alive(self)
    
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

    def try_spend_stamina(self, amount) -> bool:
        return self.try_spend_resource(Resources.STAMINA.value, amount)

class Player(Combatant):
    def __init__(self):
        super().__init__("", )
        self.gold = 0
        
    def gain_gold(self, amount):
        self.gold += amount
        
    def try_spend_gold(self, amount):
        return self.try_spend_resource(Resources.GOLD.value, amount)