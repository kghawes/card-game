import random
import utils.constants as c

class Status:
    def __init__(self, status_enum, applies_immediately):
        self.status_id = status_enum.name
        self.name = status_enum.value
        self.applies_immediately = applies_immediately

    def modify_value(self, old_value, amount, is_reduction, min_result) -> int:
        if is_reduction:
            return max(old_value - amount, min_result)
        else:
            return old_value + amount

    def trigger_on_turn(self, subject, level, status_registry=None):
        return

    def trigger_on_change(self, subject, level):
        return

    def expire(self, subject):
        return


class ModifyEffectStatus(Status):
    def __init__(
            self, status_enum, affected_cards_enum, affected_effect, 
            is_effectiveness_buff
            ):
        super().__init__(status_enum, True)
        self.affected_cards_enum = affected_cards_enum
        self.affected_effect = affected_effect
        self.sign_factor = 1 if is_effectiveness_buff else -1

    def calculate_contribution(self, level):
        """Calculate the contribution of this status to the modifier pool."""
        return self.sign_factor * c.SCALE_FACTOR * level

    def trigger_on_turn(self, subject, level, status_registry):
        """Mark cards in hand for recalculation at the start of each turn."""
        card_type = self.affected_cards_enum
        effect = self.affected_effect
        subject.recalculate_modifiers(card_type, effect)

    def trigger_on_change(self, subject, level_change):
        """Accumulate contributions to the modifier pool when level changes."""
        contribution = self.calculate_contribution(level_change)
        subject.accumulate_modifier_contribution(self, contribution)
        card_type = self.affected_cards_enum
        effect = self.affected_effect
        subject.recalculate_modifiers(card_type, effect)

    def expire(self, subject):
        """Clear contributions when the status expires."""
        subject.clear_modifier_contributions(self)


class ModifyCostStatus(Status):
    def __init__(self, status_enum, affected_cards_enum, is_cost_increase):
        super().__init__(status_enum, True)
        self.affected_cards_enum = affected_cards_enum
        self.is_cost_increase = is_cost_increase

    def trigger_on_turn(self, subject, level, status_registry):
        """Mark cards for cost recalculations at the start of each turn."""
        subject.flag_cost_recalculation(self.affected_cards_enum)

    def trigger_on_change(self, subject, level, status_registry):
        """Accumulate contributions and mark for recalculations."""
        contribution = level if self.is_cost_increase else -level
        card_type = self.affected_cards_enum
        subject.accumulate_cost_contribution(card_type, contribution)
        subject.flag_cost_recalculation(card_type)

    def expire(self, subject):
        """Clear contributions when the status expires."""
        subject.clear_cost_contributions(self.affected_cards_enum)
        subject.flag_cost_recalculation(self.affected_cards_enum)


class ModifyMaxResourceStatus(Status):
    def __init__(self, status_enum, resource_enum, is_buff):
        super().__init__(status_enum, True)
        self.resource_enum = resource_enum
        
    def trigger_on_turn(self, subject, level, status_registry):
        pass
    
    def trigger_instantly(self, subject, level) -> int:
        pass
    

class DefenseStatus(Status):
    def __init__(self):
        super().__init__(c.StatusNames.DEFENSE, False)
    
    def calculate_net_damage(
            self, subject, level, incoming_damage, status_registry
            ) -> int:
        net_damage = self.modify_value(incoming_damage, level, True, 0)
        defense_to_remove = net_damage - incoming_damage
        subject.status_manager.change_status(
            self.status_id, defense_to_remove, subject, status_registry
            )
        return net_damage


class PoisonStatus(Status):
    def __init__(self):
        super().__init__(c.StatusNames.POISON, False)
    
    def trigger_instantly(self, subject, level, status_registry):
        damage_type = c.DamageTypes.POISON
        subject.take_damage(level, damage_type, status_registry)
        
        
class EvasionStatus(Status):
    def __init__(self):
        super().__init__(c.StatusNames.EVASION, False)
    
    def calculate_evasion_damage(self, subject, level, incoming_damage) -> int:
        base_probability = c.StatusParameters.BASE_EVASION_PROBABILITY
        success_probability = min(base_probability * level, 1.0)
        roll = random.random()
        return 0 if roll >= success_probability else incoming_damage


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
        
        res_fire_status = Status(c.StatusNames.RESISTANCE_FIRE, False)
        
        ftfy_agi_status = ModifyMaxResourceStatus(
            c.StatusNames.FORTIFY_AGILITY, c.Resources.STAMINA, 
            False
            )
        dmge_agi_status = ModifyMaxResourceStatus(
            c.StatusNames.DAMAGE_AGILITY, c.Resources.STAMINA, 
            True
            )
        
        ftfy_str_status = ModifyEffectStatus(
            c.StatusNames.FORTIFY_STRENGTH, c.CardTypes.WEAPON, 
            c.EffectNames.DAMAGE.name, True
            )
        dmge_str_status = ModifyEffectStatus(
            c.StatusNames.DAMAGE_STRENGTH, c.CardTypes.WEAPON, 
            c.EffectNames.DAMAGE.name, False
            )
        
        ftfy_longblade_status = ModifyCostStatus(
            c.StatusNames.FORTIFY_LONG_BLADE, 
            c.CardSubtypes.LONG_BLADE, False
            )
        ftfy_destruction_status = ModifyCostStatus(
            c.StatusNames.FORTIFY_DESTRUCTION, 
            c.CardSubtypes.DESTRUCTION, False
            )
        
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