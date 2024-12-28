"""
This module defines the Status class, its child classes,
and the StatusRegistry.
"""
import random
import utils.constants as c

class Status:
    """The base class for an ongoing status effect."""
    def __init__(self, status_enum, applies_immediately):
        """Initialize a new Status."""
        self.status_id = status_enum.name
        self.name = status_enum.value
        self.applies_immediately = applies_immediately

    def modify_value(self, old_value, amount, is_reduction, min_result) -> int:
        """Change a given value by a given amount."""
        if is_reduction:
            return max(old_value - amount, min_result)
        return old_value + amount

    def trigger_on_turn(self, subject, level, status_registry=None):
        """Base method for polymorphism. Activate the status effect at
        the beginning of the turn."""
        return

    def trigger_on_change(self, subject, level):
        """Base method for polymorphism. Activate the status effect
        when its level is changed in order to recalculate."""
        return

    def expire(self, subject):
        """Base method for polymorphism. Clean up the status effects
        when the Status goes away."""
        return


class ModifyEffectStatus(Status):
    """Statuses that change the levels of effects on cards."""
    def __init__(
            self, status_enum, affected_cards_enum, affected_effect,
            is_effectiveness_buff
            ):
        """Initialize a new ModifyEffectStatus."""
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

    def trigger_on_change(self, subject, level):
        """Accumulate contributions to the modifier pool when level changes."""
        contribution = self.calculate_contribution(level)
        subject.accumulate_modifier_contribution(self, contribution)
        card_type = self.affected_cards_enum
        effect = self.affected_effect
        subject.recalculate_modifiers(card_type, effect)

    def expire(self, subject):
        """Clear contributions when the status expires."""
        subject.clear_modifier_contributions(self)


class ModifyCostStatus(Status):
    """Statuses that change the stamina or magicka cost on cards."""
    def __init__(self, status_enum, affected_cards_enum, is_cost_increase):
        """Initialize a new ModifyCostStatus."""
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
    """Statuses that change maximum stamina or magicka."""
    def __init__(self, status_enum, resource_enum, is_buff):
        """Initialize a new ModifyMaxResourceStatus."""
        super().__init__(status_enum, True)
        self.resource_enum = resource_enum

    def trigger_on_turn(self, subject, level, status_registry):
        pass

    def trigger_instantly(self, subject, level) -> int:
        pass


class DefenseStatus(Status):
    """This status blocks incoming damage."""
    def __init__(self):
        """Initialize a new DefenseStatus."""
        super().__init__(c.StatusNames.DEFENSE, False)

    def calculate_net_damage(
            self, subject, level, incoming_damage, status_registry
            ) -> int:
        """Return damage after blocking and handle defense reduction
        from taking damage."""
        net_damage = self.modify_value(incoming_damage, level, True, 0)
        defense_to_remove = net_damage - incoming_damage
        subject.status_manager.change_status(
            self.status_id, defense_to_remove, subject, status_registry
            )
        return net_damage


class PoisonStatus(Status):
    """This status deals Poison Damage at the start of each turn."""
    def __init__(self):
        """Initialize a new PoisonStatus."""
        super().__init__(c.StatusNames.POISON, False)

    def trigger_instantly(self, subject, level, status_registry):
        """Activate the status effect when requested by caller."""
        damage_type = c.DamageTypes.POISON
        subject.take_damage(level, damage_type, status_registry)


class EvasionStatus(Status):
    """This status randomly prevents all or zero incoming damage."""
    def __init__(self):
        """Initialize a new EvasionStatus."""
        super().__init__(c.StatusNames.EVASION, False)

    def calculate_evasion_damage(self, subject, level, incoming_damage) -> int:
        """Return the damage to be taken after winning or losing the
        dice roll."""
        base_probability = c.BASE_EVASION_PROBABILITY
        success_probability = min(base_probability * level, 1.0)
        roll = random.random()
        return 0 if roll >= success_probability else incoming_damage


class DrawStatus(Status):
    """Statuses that affect the number of cards drawn per turn."""
    def __init__(self, status_enum, is_buff):
        """Initialize a new DrawStatus"""
        super().__init__(status_enum, False)

    def trigger_instantly(self, subject, level):
        """Activate the status effect when requested by the caller."""
        pass


class StatusRegistry:
    """Holds Status objects in a dictionary to be looked up when 
    needed."""
    def __init__(self):
        """Initialize a new StatusRegistry."""
        self.statuses = self._initialize_statuses()

    def _initialize_statuses(self) -> dict:
        """Create Status objects and file them in a dict."""
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
        """Get Status object by status id."""
        if status_id not in self.statuses:
            raise KeyError(f"Status ID '{status_id}' not found.")
        return self.statuses[status_id]

    def list_statuses(self) -> list:
        """Return a list of status ids."""
        return list(self.statuses.keys())
