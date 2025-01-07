"""
This module defines the Status class, its child classes,
and the StatusRegistry.
"""
import random
import utils.constants as c
from utils.utils import load_json

class Status:
    """The base class for an ongoing status effect."""
    def __init__(self, status_id, applies_immediately):
        """Initialize a new Status."""
        self.status_id = status_id
        self.name = c.StatusNames[status_id].value
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
            self, status_id, affected_card_type, affected_effect,
            sign_factor
            ):
        """Initialize a new ModifyEffectStatus."""
        super().__init__(status_id, True)
        self.affected_card_type = affected_card_type
        self.affected_effect = affected_effect
        self.sign_factor = sign_factor

    def calculate_contribution(self, level):
        """Calculate the contribution of this status to the modifier pool."""
        return self.sign_factor * c.SCALE_FACTOR * level

    def trigger_on_turn(self, subject, level, status_registry):
        """Recalculate effects at the start of each turn."""
        card_type = self.affected_card_type
        effect = self.affected_effect
        subject.modifier_manager.recalculate_effect_modifiers(
            card_type, effect, subject.card_manager
            )

    def trigger_on_change(self, subject, level):
        """Accumulate contributions to the modifier pool when level changes."""
        contribution = self.calculate_contribution(level)
        subject.modifier_manager.accumulate_effect_modifier(self, contribution)
        card_type = self.affected_card_type
        effect = self.affected_effect
        subject.modifier_manager.recalculate_effect_modifiers(
            card_type, effect, subject.card_manager
            )

    def expire(self, subject):
        """Clear contributions when the status expires."""
        subject.modifier_manager.clear_effect_modifiers(
            self, subject.card_manager
            )


class ModifyCostStatus(Status):
    """Statuses that change the stamina or magicka cost on cards."""
    def __init__(self, status_id, affected_card_type, sign_factor):
        """Initialize a new ModifyCostStatus."""
        super().__init__(status_id, True)
        self.affected_card_type = affected_card_type
        self.sign_factor = sign_factor

    def calculate_contribution(self, level):
        """Calculate the contribution of this status to the modifier pool."""
        return self.sign_factor * level

    def trigger_on_turn(self, subject, level, status_registry):
        """Recalculate costs at the start of each turn."""
        card_type = self.affected_card_type
        subject.modifier_manager.recalculate_cost_modifiers(
            card_type, subject.card_manager
            )

    def trigger_on_change(self, subject, level):
        """Accumulate contributions to the modifier pool when level changes."""
        contribution = self.calculate_contribution(level)
        subject.modifier_manager.accumulate_cost_modifier(self, contribution)
        card_type = self.affected_card_type
        subject.modifier_manager.recalculate_cost_modifiers(
            card_type, subject.card_manager
            )

    def expire(self, subject):
        """Clear contributions when the status expires."""
        subject.modifier_manager.clear_cost_modifiers(
            self, subject.card_manager
            )


class ModifyMaxResourceStatus(Status):
    """Statuses that change maximum stamina or magicka."""
    def __init__(self, status_id, resource_id, sign_factor):
        """Initialize a new ModifyMaxResourceStatus."""
        super().__init__(status_id, True)
        self.resource_id = resource_id
        self.sign_factor = sign_factor

    def trigger_on_change(self, subject, level):
        modifier_manager = subject.modifier_manager
        amount = level * self.sign_factor
        modifier_manager.modify_max_resource(
            subject.resources[self.resource_id], self.status_id, amount
            )


class ModifyDrawStatus(Status):
    """Statuses that affect the number of cards drawn per turn."""
    def __init__(self, status_id, sign_factor):
        """Initialize a new DrawStatus"""
        super().__init__(status_id, True)
        self.sign_factor = sign_factor

    def trigger_on_change(self, subject, level):
        """Update the modifier pool with the new contribution."""
        modifier_manager = subject.modifier_manager
        amount = level * self.sign_factor
        modifier_manager.modify_cards_to_draw(self.status_id, amount)


class ModifyDamageStatus(Status):
    """Stasuses that affect the amount of damage taken."""
    def __init__(self, status_id, damage_type, sign_factor):
        """Initialize a new ModifyDamageStatus."""
        super().__init__(status_id, True)
        self.damage_type = damage_type
        self.sign_factor = sign_factor

    def trigger_on_change(self, subject, level):
        """Update the modifier pool with the new contribution."""
        modifier_manager = subject.modifier_manager
        amount = level * self.sign_factor * c.SCALE_FACTOR
        modifier_manager.accumulate_damage_modifier(self.status_id, amount)


class DefenseStatus(Status):
    """This status blocks incoming damage."""
    def __init__(self, status_id):
        """Initialize a new DefenseStatus."""
        super().__init__(status_id, False)

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
    def __init__(self, status_id):
        """Initialize a new PoisonStatus."""
        super().__init__(status_id, False)

    def trigger_on_turn(self, subject, level, status_registry):
        """Activate the status effect when requested by caller."""
        damage_type = c.DamageTypes.POISON.name
        subject.take_damage(level, damage_type, status_registry)


class RegenerationStatus(Status):
    """This status restores health at the start of each turn."""
    def __init__(self, status_id):
        """Initialize a new RegenerationStatus."""
        super().__init__(status_id, False)

    def trigger_on_turn(self, subject, level, status_registry):
        subject.change_resource(c.Resources.HEALTH.name, level)


class EvasionStatus(Status):
    """This status randomly prevents all or zero incoming damage."""
    def __init__(self, status_id):
        """Initialize a new EvasionStatus."""
        super().__init__(status_id, False)

    def calculate_evasion_damage(self, level, incoming_damage) -> int:
        """Return the damage to be taken after winning or losing the
        dice roll."""
        base_probability = c.BASE_EVASION_PROBABILITY
        success_probability = min(base_probability * level, 1.0)
        roll = random.random()
        return 0 if roll >= success_probability else incoming_damage


class RestrictCardTypeStatus(Status):
    """This status prevents the subject from playing certain tyoes of
    cards."""
    def __init__(self, status_id, restricted_types):
        """Initialize a new RestrictCardStatus."""
        super().__init__(status_id, True)
        self.restricted_types = restricted_types

    def is_card_playable(self, card_type) -> bool:
        """Check if the given card type is allowed to be played."""
        return card_type not in self.restricted_types


class FilterEffectStatus(Status):
    """This status allows only certain effects to resolve."""
    def __init__(self, status_id, allowed_effect, blocked_effect):
        """Initialize a new FilterEffectStatus."""
        super().__init__(status_id, False)
        self.allowed_effect = allowed_effect
        self.blocked_effect = blocked_effect

    def effect_can_resolve(self, effect_id) -> bool:
        """Check if the given effect is allowed to resolve."""
        if self.blocked_effect and effect_id == self.blocked_effect:
            return False
        if self.allowed_effect and effect_id != self.allowed_effect:
            return False
        return True


class LimitCardPlayStatus(Status):
    """This status prevents a combatant from playing more than a
    certain number of cards per turn."""
    def __init__(self, status_id, max_cards_per_turn):
        """Initialize a new LimitCardPlayStatus."""
        super().__init__(status_id, False)
        self.card_limit = max_cards_per_turn


class StatusRegistry:
    """Holds Status objects in a dictionary to be looked up when 
    needed."""
    def __init__(self, statuses_path):
        """Initialize a new StatusRegistry."""
        self.statuses = self._initialize_statuses(statuses_path)

    def _initialize_statuses(self, filepath) -> dict:
        """Create Status objects and file them in a dict."""
        status_data = load_json(filepath)
        status_classes = {
            "Status": Status,
            "ModifyEffectStatus": ModifyEffectStatus,
            "ModifyCostStatus": ModifyCostStatus,
            "ModifyMaxResourceStatus": ModifyMaxResourceStatus,
            "ModifyDrawStatus": ModifyDrawStatus,
            "ModifyDamageStatus": ModifyDamageStatus,
            "DefenseStatus": DefenseStatus,
            "PoisonStatus": PoisonStatus,
            "RegenerationStatus": RegenerationStatus,
            "EvasionStatus": EvasionStatus,
            "RestrictCardTypeStatus": RestrictCardTypeStatus,
            "FilterEffectStatus": FilterEffectStatus
            }

        statuses = {}

        for status_id, data in status_data.items():
            class_name = data.pop("class") # Extract the class name
            if class_name not in status_classes:
                raise ValueError(f"Unknown status class: {class_name}")

            # Instantiate the status dynamically
            status_class = status_classes[class_name]
            data["status_id"] = status_id
            statuses[status_id] = status_class(**data)

        return statuses

    def get_status(self, status_id) -> Status:
        """Get Status object by status id."""
        if status_id not in self.statuses:
            raise KeyError(f"Status ID '{status_id}' not found.")
        return self.statuses[status_id]

    def list_statuses(self) -> list:
        """Return a list of status ids."""
        return list(self.statuses.keys())
