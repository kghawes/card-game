from gameplay.card_manager import CardManager
from gameplay.status_manager import StatusManager
from utils.constants import StatusNames, Resources, MIN_RESOURCE, SCALE_FACTOR

class Combatant:
    def __init__(self, name, max_health, max_stamina, max_magicka, starting_deck, card_cache):
        self.name = name
        self.resources = {
            Resources.HEALTH.name: Resource(Resources.HEALTH, max_health),
            Resources.STAMINA.name: Resource(Resources.STAMINA, max_stamina),
            Resources.MAGICKA.name: Resource(Resources.MAGICKA, max_magicka)
        }
        self.card_manager = CardManager(starting_deck, card_cache)
        self.status_manager = StatusManager()
        
    def get_health(self) -> int:
        return self.resources[Resources.HEALTH.name].current_value
    
    def get_max_health(self) -> int:
        return self.resources[Resources.HEALTH.name].get_max_value()
    
    def get_stamina(self) -> int:
        return self.resources[Resources.STAMINA.name].current_value
    
    def get_max_stamina(self) -> int:
        return self.resources[Resources.STAMINA.name].get_max_value()
    
    def get_magicka(self) -> int:
        return self.resources[Resources.MAGICKA.name].current_value
    
    def get_max_magicka(self) -> int:
        return self.resources[Resources.MAGICKA.name].get_max_value()
        
    def take_damage(self, amount, damage_type_enum, status_registry) -> bool:
        
        amount = self.apply_resistances_and_weaknesses(amount, damage_type_enum.name)
        
        if self.status_manager.has_status(StatusNames.DEFENSE.name, self, status_registry):
            defense_status = status_registry.get_status(StatusNames.DEFENSE.name)
            defense_level = self.status_manager.get_status_level(StatusNames.DEFENSE.name)
            amount = defense_status.calculate_net_damage(self, defense_level, amount, status_registry)
            
        self.resources[Resources.HEALTH.name].change_value(-1 * amount)
        return self.is_alive()
    
    def apply_resistances_and_weaknesses(self, damage_amount, incoming_damage_type) -> int:
        multiplier = 1
        
        for active_status_id, status_level in self.status_manager.statuses.items():
            sign_factor = 1
            if StatusNames.RESISTANCE.name in active_status_id:
                sign_factor = -1
            elif StatusNames.WEAKNESS.name not in active_status_id:
                continue
            if incoming_damage_type in active_status_id:
                multiplier += sign_factor * status_level * SCALE_FACTOR
                        
        return round(damage_amount * multiplier)
    
    def is_alive(self) -> bool:
        return self.get_health() > 0
    
    def replenish_resources_for_turn(self):
        self.resources[Resources.STAMINA.name].replenish()
        self.resources[Resources.MAGICKA.name].replenish()
    
    def reset_for_turn(self):
        self.card_manager.reset_cards_to_draw()
        self.replenish_resources_for_turn()
        
    def change_resource(self, resource_id, amount):
        assert resource_id != Resources.HEALTH or amount >= 0 #
        self.resources[resource_id].change_value(amount)


class Resource:
    def __init__(self, resource_enum, max_value):
        self.resource_enum = resource_enum
        self.max_value = max_value
        self.modified_max_value = max_value
        self.current_value = max_value
        
    def change_value(self, amount):
        self.current_value = min(max(self.current_value + amount, 0), self.modified_max_value)
    
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