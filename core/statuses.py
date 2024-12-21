import random
from utils.constants import CardTypes, CardSubtypes, StatusNames, DamageTypes, StatusParameters
import gameplay.modifiers as modifiers

class Status:
    def __init__(self, status_enum):
        self.status_id = status_enum.name
        self.name = status_enum.value
    
    def trigger_on_turn(self, subject, level):
        # Perform the actions the status needs done
        return
    
    def trigger_instantly(self, subject, level, *args, **kwargs) -> int:
        return kwargs.get("default", 0)

class DefenseStatus(Status):
    def __init__(self):
        super().__init__(StatusNames.DEFENSE)
        self.modifier = modifiers.FlatModifier(StatusNames.DEFENSE)
    
    def trigger_instantly(self, subject, level, *args, **kwargs) -> int:
        incoming_damage = kwargs.get("incoming_damage", 0)
        net_damage = self.modifier.modify_value(level, incoming_damage)
        defense_to_remove = net_damage - incoming_damage
        subject.status_manager.change_status(self.status_id, defense_to_remove)
        return net_damage

class PoisonStatus(Status):
    def __init__(self):
        super().__init__(StatusNames.POISON)
    
    def trigger_on_turn(self, subject, level):
        subject.take_damage(level, DamageTypes.POISON)
        
class EvasionStatus(Status):
    def __init__(self):
        super().__init__(StatusNames.EVASION)
    
    def trigger_instantly(self, subject, level, *args, **kwargs) -> int:
        incoming_damage = kwargs.get("damage", 0)
        success_probability = min(StatusParameters.BASE_EVASION_PROBABILITY * level, 1.0)
        roll = random.random()
        return 0 if roll >= success_probability else incoming_damage

class ModifyCostStatus(Status):
    def __init__(self, status_enum, affected_cards_enum, is_cost_increase):
        super().__init__(status_enum)
        self.affected_cards_enum = affected_cards_enum
        self.is_cost_increase = is_cost_increase
        self.modifier = modifiers.FlatModifier(status_enum, is_cost_increase)
        
    def trigger_on_turn(self, subject, level):
        for card in subject.card_manager.hand:
            if card.matches(self.status_enum):
                card.set_cost(self.modifier.modify_value(level, card.get_cost()))

class StatusRegistry:
    def __init__(self, statuses_path):
        self.statuses = self._initialize_statuses()
    
    def _initialize_statuses(self) -> dict:
        defense_status = DefenseStatus()
        poison_status = PoisonStatus()
        
        ftfy_agi_status = ModifyCostStatus(StatusNames.FORTIFY_AGILITY, CardTypes.SKILL, False)
        dmge_agi_status = ModifyCostStatus(StatusNames.DAMAGE_AGILITY, CardTypes.SKILL, True)
        
        ftfy_longblade_status = ModifyCostStatus(StatusNames.FORTIFY_LONG_BLADE, CardSubtypes.LONG_BLADE, False)
        ftfy_destruction_status = ModifyCostStatus(StatusNames.FORTIFY_DESTRUCTION, CardSubtypes.DESTRUCTION, False)
        
        return {
            defense_status.status_id: defense_status,
            poison_status.status_id: poison_status,
            ftfy_agi_status.status_id: ftfy_agi_status,
            dmge_agi_status.status_id: dmge_agi_status,
            ftfy_longblade_status.status_id: ftfy_longblade_status,
            ftfy_destruction_status.status_id: ftfy_destruction_status
        }
    
    def get_status(self, status_id) -> Status:
        if status_id not in self.statuses:
            raise KeyError(f"Status ID '{status_id}' not found.")
        return self.statuses[status_id]