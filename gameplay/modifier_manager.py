import utils.constants as c
"""
This module defined the ModifierManager class and modifier classes.
"""
from core.statuses import ModifyEffectStatus, ModifyMaxResourceStatus, \
    ModifyDrawStatus, ModifyDamageStatus

class ModifierManager:
    """This class holds the details of currently active status
    modifications and controls their update and application."""
    def __init__(self, status_registry):
        """Initialize a new ModifierManager."""
        self.effect_modifiers = self._initialize_effect_modifiers(
            status_registry
            )
        self.resource_modifiers = self._initialize_resource_modifiers(
            status_registry
            )
        self.draw_modifiers = self._initialize_draw_modifiers(
            status_registry
            )
        self.damage_modifiers = self._initialize_damage_modifiers(
            status_registry
            )

    def reset_modifier_pool(self, modifier_pool):
        """Clear all active modifiers for all statuses of a certain
        type."""
        for modifier in modifier_pool.values():
            modifier.reset()

    def reset_all(self):
        """Clear all active modifiers for all statuses."""
        self.reset_modifier_pool(self.effect_modifiers)
        self.reset_modifier_pool(self.resource_modifiers)
        self.reset_modifier_pool(self.draw_modifiers)

    # Effect modifiers

    def _initialize_effect_modifiers(self, status_registry) -> dict:
        """Populate the effect modifier pool with statuses."""
        effect_modifiers = {} # Tracks accumulated contributions by status
        for status_id, status in status_registry.statuses.items():
            if isinstance(status, ModifyEffectStatus):
                card_type = status.affected_card_type
                effect = status.affected_effect
                effect_modifiers[status_id] = EffectModifier(card_type, effect)
        return effect_modifiers

    def accumulate_effect_modifier(self, status, contribution):
        """Accumulate contributions to effect modifiers in the pool."""
        old_value = self.effect_modifiers[status.status_id].contribution
        new_value = old_value + contribution
        self.effect_modifiers[status.status_id].contribution = new_value

    def clear_effect_modifiers(self, status, card_manager):
        """Clear contributions for a specific status."""
        if isinstance(status, ModifyEffectStatus):
            self.effect_modifiers[status.status_id].contribution = 0
            card_type = status.affected_card_type
            effect = status.affected_effect
            self.recalculate_effect_modifiers(card_type, effect, card_manager)

    def reset_effect_modifiers(self, card_type, effect, card_manager):
        """Set effect modifiers affecting this card type and effect to 0."""
        for card in card_manager.hand:
            if card.matches(card_type):
                self.reset_card_effect(card, effect)

    def recalculate_effect_modifiers(self, card_type, effect, card_manager):
        """Recalculate affected effect modifiers for affected cards."""
        self.reset_effect_modifiers(card_type, effect, card_manager)
        for modifier in self.effect_modifiers.values():
            if modifier.matches(card_type, effect):
                for card in card_manager.hand:
                    if card.matches(card_type):
                        self.modify_card_effect(card, effect, modifier)

    def recalculate_all_effects(self, status_registry, card_manager):
        """Recalculate all effect modifiers for all cards."""
        for status_id in status_registry.list_statuses():
            status = status_registry.get_status(status_id)
            if isinstance(status, ModifyEffectStatus):
                card_type = status.affected_card_type
                effect = status.affected_effect
                self.recalculate_effect_modifiers(
                    card_type, effect, card_manager
                    )

    def modify_card_effect(self, card, effect, modifier):
        """Change the effect level of the given effect on this card."""
        for effect_id, effect_level in card.effects.items():
            if effect in effect_id:
                amount = modifier.contribution
                effect_level.change_level(amount)

    def reset_card_effect(self, card, effect):
        """Reset the effect level of the given effect on this card."""
        for effect_id, effect_level in card.effects.items():
            if effect in effect_id:
                effect_level.reset_level()

    # Max resource modifiers

    def _initialize_resource_modifiers(self, status_registry) -> dict:
        """Populate the resource modifier pool with statuses."""
        resource_modifiers = {} # Tracks accumulated contributions by status
        for status_id, status in status_registry.statuses.items():
            if isinstance(status, ModifyMaxResourceStatus):
                resource_modifiers[status_id] = ResourceModifier(
                    status.resource_id
                    )
        return resource_modifiers
    
    def reset_max_resource(self, resource_id):
        """Clear all modifiers for the resource and reset maximum
        value to its base value."""
        for modifier in self.resource_modifiers.values():
            if modifier.matches(resource_id):
                 modifier.contribution = 0

    def clear_resource_modifiers(self, status_id):
        """Remove max value modifier contribution from a specific
        status."""
        if status_id in self.resource_modifiers:
            self.resource_modifiers[status_id] = 0

    def get_max_resource(self, resource_id, base_max_value) -> int:
        """Get the (modified) maximum value of the resource."""
        net_contribution = 0
        for modifier in self.resource_modifiers.values():
            if modifier.matches(resource_id):
                net_contribution += modifier.contribution
        return max(base_max_value + net_contribution, c.MIN_RESOURCE)

    def modify_max_resource(self, resource, status_id, amount):
        """Change the maximum value by the given amount."""
        if status_id in self.resource_modifiers:
            old_value = self.resource_modifiers[status_id].contribution
            new_value = old_value + amount
            self.resource_modifiers[status_id].contribution = new_value
            resource.change_value(amount, self)

    # Draw modifiers

    def _initialize_draw_modifiers(self, status_registry) -> dict:
        """Populate the resource modifier pool with statuses."""
        draw_modifiers = {} # Tracks accumulated contributions by status
        for status_id, status in status_registry.statuses.items():
            if isinstance(status, ModifyDrawStatus):
                draw_modifiers[status_id] = DrawModifier()
        return draw_modifiers

    def modify_cards_to_draw(self, status_id, amount):
        """Change the number of cards to draw by the given amount."""
        if status_id in self.draw_modifiers:
            old_value = self.draw_modifiers[status_id].contribution
            new_value = old_value + amount
            self.draw_modifiers[status_id].contribution = new_value

    def calculate_cards_to_draw(self) -> int:
        """Get the modified number of cards to draw for a turn."""
        net_contribution = 0
        for modifier in self.draw_modifiers.values():
            net_contribution += modifier.contribution
        return max(c.HAND_SIZE + net_contribution, c.MIN_HAND_SIZE)

    # Damage modifiers

    def _initialize_damage_modifiers(self, status_registry) -> dict:
        damage_modifiers = {}
        for status_id, status in status_registry.statuses.items():
            if isinstance(status, ModifyDamageStatus):
                modifier = DamageModifier(status.damage_type)
                damage_modifiers[status_id] = modifier
        return damage_modifiers

    def accumulate_damage_modifier(self, status_id, contribution):
        """Update the contribution amount in the modifier pool."""
        old_value = self.damage_modifiers[status_id].contribution
        new_value = old_value + contribution
        self.damage_modifiers[status_id].contribution = new_value

    def calculate_damage(self, damage_type, amount):
        net_contribution = 0
        for modifier in self.damage_modifiers.values():
            if modifier.matches(damage_type):
                net_contribution += modifier.contribution
        return round((1 + net_contribution) * amount)


# Modifier classes

class Modifier:
    """This is the base class representing a modifier that comes from
    an active status."""
    def __init__(self):
        """Initialize a new Modifier."""
        self.contribution = 0

    def reset(self):
        """Reset this modifier's contribution to 0."""
        self.contribution = 0


class EffectModifier(Modifier):
    """This class represents a modifier that applies to all cards of a
    specified type and modifies the level of the specified effect on
    those cards."""
    def __init__(self, affected_card_type, affected_effect_id):
        """Initialize a new EffectModifier."""
        super().__init__()
        self.card_type = affected_card_type
        self.effect_id = affected_effect_id

    def matches(self, card_type, effect_id) -> bool:
        """Checks if the given card type and effect are subject to
        this modifier."""
        matches_type = self.card_type == card_type
        matches_effect = self.effect_id == effect_id
        return matches_type and matches_effect


class ResourceModifier(Modifier):
    """This class represents a modifier that changes the maximum value
    of a resource."""
    def __init__(self, resource_id):
        """Initialize a new ResourceModifier."""
        super().__init__()
        self.resource_id = resource_id

    def matches(self, resource_id) -> bool:
        """Checks if the given resource is subject to this modifier."""
        return self.resource_id == resource_id


class DrawModifier(Modifier):
    """This class represents a modifier that changes the number of
    cards drawn at the beginning of each turn."""
    def __init__(self):
        """Initialize a new DrawModifier."""
        super().__init__()


class DamageModifier(Modifier):
    """This class represents a modifier that changes the amount of
    incoming damage based on its damage type."""
    def __init__(self, damage_type):
        """Initialize a new DamageModifier."""
        super().__init__()
        self.damage_type = damage_type

    def matches(self, damage_type):
        """Checks if the given damage type is subject to this modifier."""
        return damage_type == self.damage_type
