import random
import utils.constants as constants

class Status:
    def __init__(self, status_enum, applies_immediately):
        self.status_id = status_enum.name
        self.name = status_enum.value
        self.applies_immediately = applies_immediately
        
    def modify_value_flat(self, old_value, change_amount, is_reduction, minimum_result) -> int:
        if is_reduction:
            return max(old_value - change_amount, minimum_result)
        else:
            return old_value + change_amount
    
    def modify_value_scaling(self, old_value, status_level, is_reduction, minimum_result) -> int:
        sign_factor = -1 if is_reduction else 1
        new_value_exact = (1 + sign_factor * constants.SCALE_FACTOR * status_level) * old_value
        return round(new_value_exact)
    
    def trigger_on_turn(self, subject, level):
        return
    
    def trigger_on_apply(self, subject, level):
        return

class DefenseStatus(Status):
    def __init__(self):
        super().__init__(constants.StatusNames.DEFENSE, False)
    
    def trigger_instantly(self, subject, level, incoming_damage) -> int:
        net_damage = self.modify_value_flat(incoming_damage, level, True, 0)
        defense_to_remove = net_damage - incoming_damage
        subject.status_manager.change_status(self.status_id, defense_to_remove)
        return net_damage

class PoisonStatus(Status):
    def __init__(self):
        super().__init__(constants.StatusNames.POISON, False)
    
    def trigger_on_turn(self, subject, level):
        subject.take_damage(level, constants.DamageTypes.POISON)
        
class EvasionStatus(Status):
    def __init__(self):
        super().__init__(constants.StatusNames.EVASION, False)
    
    def trigger_instantly(self, subject, level, incoming_damage) -> int:
        success_probability = min(constants.StatusParameters.BASE_EVASION_PROBABILITY * level, 1.0)
        roll = random.random()
        return 0 if roll >= success_probability else incoming_damage

class ModifyCostStatus(Status):
    def __init__(self, status_enum, affected_cards_enum, is_cost_increase):
        super().__init__(status_enum, True)
        self.affected_cards_enum = affected_cards_enum
        self.is_cost_increase = is_cost_increase
        
    def trigger_on_turn(self, subject, level):
        for card in subject.card_manager.hand:
            self.trigger_instantly(subject, level, card)
    
    def trigger_instantly(self, subject, level, card):
        if card.matches(self.affected_cards_enum):
            card.set_cost(self.modifier.modify_value(level, card.get_cost()))###########################################################
    
    def trigger_on_apply(self, subject, level):
        self.trigger_on_turn(subject, level)

class ModifyEffectStatus(Status):
    def __init__(self, status_enum, affected_cards_enum, affected_effect, is_effectiveness_buff):
        super().__init__(status_enum, True)
        self.affected_cards_enum = affected_cards_enum
        self.affected_effect = affected_effect
        self.is_reduction = not is_effectiveness_buff
        
    def trigger_on_turn(self, subject, level):
        for card in subject.card_manager.hand:
            self.trigger_instantly(subject, level, card)
    
    def trigger_instantly(self, subject, level, card):
        if card.matches(self.affected_cards_enum):
            for effect_id, effect_level in card.effects.items():
                if self.affected_effect in effect_id:
                    new_level = self.modify_value_scaling(effect_level.get_level(), level, self.is_reduction, constants.MIN_EFFECT)
                    effect_level.set_level(new_level)
    
    def trigger_on_apply(self, subject, level):
        self.trigger_on_turn(subject, level)

class ModifyMaxResourceStatus(Status):
    def __init__(self, status_enum, resource_enum, is_buff):
        super().__init__(status_enum, True)
        self.resource_enum = resource_enum
        
    def trigger_on_turn(self, subject, level):
        pass
    
    def trigger_instantly(self, subject, level) -> int:
        pass

class SpeedStatus(Status):
    def __init__(self, status_enum, is_buff):
        super().__init__(status_enum, False)
    
    def trigger_instantly(self, subject, level):
        pass
        
class StatusRegistry:
    def __init__(self, statuses_path):
        self.statuses = self._initialize_statuses()
    
    def _initialize_statuses(self) -> dict:
        defense_status = DefenseStatus()
        poison_status = PoisonStatus()
        
        res_fire_status = Status(constants.StatusNames.RESISTANCE_FIRE, False)
        
        ftfy_agi_status = ModifyCostStatus(constants.StatusNames.FORTIFY_AGILITY, constants.CardTypes.SKILL, False)
        dmge_agi_status = ModifyCostStatus(constants.StatusNames.DAMAGE_AGILITY, constants.CardTypes.SKILL, True)
        
        ftfy_str_status = ModifyEffectStatus(constants.StatusNames.FORTIFY_STRENGTH, constants.CardTypes.WEAPON, constants.EffectNames.DAMAGE.name, True)
        dmge_str_status = ModifyEffectStatus(constants.StatusNames.DAMAGE_STRENGTH, constants.CardTypes.WEAPON, constants.EffectNames.DAMAGE.name, False)
        
        ftfy_longblade_status = ModifyCostStatus(constants.StatusNames.FORTIFY_LONG_BLADE, constants.CardSubtypes.LONG_BLADE, False)
        ftfy_destruction_status = ModifyCostStatus(constants.StatusNames.FORTIFY_DESTRUCTION, constants.CardSubtypes.DESTRUCTION, False)
        
        return {
            defense_status.status_id: defense_status,
            poison_status.status_id: poison_status,
            res_fire_status.status_id: res_fire_status,
            ftfy_agi_status.status_id: ftfy_agi_status,
            dmge_agi_status.status_id: dmge_agi_status,
            ftfy_str_status.status_id: ftfy_str_status,
            dmge_str_status.status_id: dmge_str_status,
            ftfy_longblade_status.status_id: ftfy_longblade_status,
            ftfy_destruction_status.status_id: ftfy_destruction_status
        }
    
    def get_status(self, status_id) -> Status:
        if status_id not in self.statuses:
            raise KeyError(f"Status ID '{status_id}' not found.")
        return self.statuses[status_id]
    
    def list_statuses(self) -> list:
        return list(self.statuses.keys())