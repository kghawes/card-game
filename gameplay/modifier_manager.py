"""
This module defines the ModifierManager class and modifier classes.
"""
import utils.constants as c
from core.statuses import ModifyEffectStatus, ModifyMaxResourceStatus, \
    ModifyDrawStatus, ModifyDamageStatus, ModifyCostStatus

class ModifierManager:
    """
    This class holds the details of currently active status modifiers and
    controls their update and application.

    Modifiers are grouped by type, and each type has its own pool of
    modifiers. For example, damage modifiers include specific weaknesses and
    resistances. Each modifier lists contributions by status id, and the
    ModifierManager is responsible for accumulating these contributions and
    applying them to the game state.
    """
    def __init__(self, status_registry):
        """
        Initialize a new ModifierManager.
        """
        # self.effect_modifiers = self._initialize_effect_modifiers(status_registry)
        self.resource_modifiers = self._initialize_resource_modifiers(status_registry)
        self.draw_modifiers = self._initialize_draw_modifiers(status_registry)
        self.damage_modifiers = self._initialize_damage_modifiers(status_registry)
        self.cost_modifiers = self._initialize_cost_modifiers(status_registry)
        self.modifier_pools = [
            # self.effect_modifiers,
            self.resource_modifiers,
            self.draw_modifiers,
            self.cost_modifiers,
            self.damage_modifiers
            ]

    def reset_modifier_pool(self, modifier_pool):
        """
        Clear all active modifiers of a certain type, defined by the given pool.
        modifier_pool: dict
            The pool of modifiers to reset.
        """
        for modifier in modifier_pool.values():
            modifier.reset()

    def reset_all(self):
        """
        Clear all active modifiers of all types.
        """
        for pool in self.modifier_pools:
            self.reset_modifier_pool(pool)

    # Effect modifiers

    # def _initialize_effect_modifiers(self, status_registry) -> dict:
    #     """
    #     Populate the effect modifier pool with statuses and attributes.
    #     """
    #     effect_modifiers = {} # Tracks accumulated contributions by source
    #     for status_id, status in status_registry.statuses.items():
    #         if isinstance(status, ModifyEffectStatus):
    #             card_type = status.affected_card_type
    #             effect = status.affected_effect
    #             effect_modifiers[status_id] = EffectModifier(card_type, effect)
    #     # 
    #     return effect_modifiers

    # def accumulate_effect_modifier(self, status, contribution):
    #     """
    #     Accumulate contributions to effect modifiers in the pool.
    #     """
    #     old_value = self.effect_modifiers[status.status_id].contribution
    #     new_value = old_value + contribution
    #     self.effect_modifiers[status.status_id].contribution = new_value

    # def clear_effect_modifiers(self, status, card_manager):
    #     """
    #     Clear contributions for a specific status.
    #     """
    #     if isinstance(status, ModifyEffectStatus):
    #         self.effect_modifiers[status.status_id].contribution = 0
    #         card_type = status.affected_card_type
    #         effect = status.affected_effect
    #         self.recalculate_effect_modifiers(card_type, effect, card_manager)

    # def reset_effect_modifiers(self, card_type, effect, card_manager):
    #     """
    #     Set effect modifiers affecting this card type and effect to 0.
    #     """
    #     for card in card_manager.hand:
    #         if card.matches(card_type):
    #             self.reset_card_effect(card, effect)

    # def recalculate_effect_modifiers(self, card_type, effect, card_manager):
    #     """
    #     Recalculate affected effect modifiers for affected cards.
    #     """
    #     self.reset_effect_modifiers(card_type, effect, card_manager)
    #     for modifier in self.effect_modifiers.values():
    #         if modifier.matches(card_type, effect):
    #             for card in card_manager.hand:
    #                 if card.matches(card_type):
    #                     self.modify_card_effect(card, effect, modifier)

    # def recalculate_all_effects(self, status_registry, card_manager):
    #     """
    #     Recalculate all effect modifiers for all cards.
    #     """
    #     for status_id in status_registry.list_statuses():
    #         status = status_registry.get_status(status_id)
    #         if isinstance(status, ModifyEffectStatus):
    #             card_type = status.affected_card_type
    #             effect = status.affected_effect
    #             self.recalculate_effect_modifiers(
    #                 card_type, effect, card_manager
    #                 )

    # def modify_card_effect(self, card, effect_id, modifier):
    #     """
    #     Change the effect level modifier of the given effect on this card.
    #     """
    #     for effect in card.effects:
    #         if effect_id in effect.str_id or effect_id == c.EffectNames.ALL_EFFECTS.name:
    #             amount = modifier.contribution
    #             effect.change_level_modifier(amount)

    # def reset_card_effect(self, card, effect_id):
    #     """
    #     Reset the effect level of the given effect on this card.
    #     """
    #     for effect in card.effects:
    #         if effect_id in effect.str_id or effect_id == c.EffectNames.ALL_EFFECTS.name:
    #             effect.reset_level()

    # Max resource modifiers

    def _initialize_resource_modifiers(self, status_registry) -> dict:
        """
        Populate the resource modifier pool with statuses.
        """
        resource_modifiers = {} # Tracks accumulated contributions by status
        for status_id, status in status_registry.statuses.items():
            if isinstance(status, ModifyMaxResourceStatus):
                resource_modifiers[status_id] = ResourceModifier(
                    status.resource_id
                    )
        return resource_modifiers

    def reset_max_resource(self, resource_id):
        """
        Clear all modifiers for the resource and reset maximum value to its
        base value.
        """
        for modifier in self.resource_modifiers.values():
            if modifier.matches(resource_id):
                modifier.contribution = 0

    def clear_resource_modifiers(self, status_id):
        """
        Remove max value modifier contribution from a specific status.
        """
        if status_id in self.resource_modifiers:
            self.resource_modifiers[status_id].contribution = 0

    def get_max_resource(self, resource_id, base_max_value) -> int:
        """
        Get the (modified) maximum value of the resource.
        """
        net_contribution = 0
        for modifier in self.resource_modifiers.values():
            if modifier.matches(resource_id):
                net_contribution += modifier.contribution
        return max(base_max_value + net_contribution, c.MIN_RESOURCE)

    def modify_max_resource(self, resource, status_id, amount):
        """
        Change the maximum value by the given amount.
        """
        if status_id in self.resource_modifiers:
            old_value = self.resource_modifiers[status_id].contribution
            new_value = old_value + amount
            self.resource_modifiers[status_id].contribution = new_value
            resource.change_value(amount, self)

    # Draw modifiers

    def _initialize_draw_modifiers(self, status_registry) -> dict:
        """
        Populate the resource modifier pool with statuses.
        """
        draw_modifiers = {} # Tracks accumulated contributions by status
        for status_id, status in status_registry.statuses.items():
            if isinstance(status, ModifyDrawStatus):
                draw_modifiers[status_id] = Modifier()
        return draw_modifiers

    def modify_cards_to_draw(self, status_id, amount):
        """
        Change the number of cards to draw by the given amount.
        """
        if status_id in self.draw_modifiers:
            old_value = self.draw_modifiers[status_id].contribution
            new_value = old_value + amount
            self.draw_modifiers[status_id].contribution = new_value

    def calculate_cards_to_draw(self) -> int:
        """
        Get the modified number of cards to draw for a turn.
        """
        net_contribution = 0
        for modifier in self.draw_modifiers.values():
            net_contribution += modifier.contribution
        return max(c.HAND_SIZE + net_contribution, c.MIN_HAND_SIZE)

    # Damage modifiers

    def _initialize_damage_modifiers(self, status_registry) -> dict:
        """
        Populate the modifier pool with statuses.
        """
        damage_modifiers = {}
        for status_id, status in status_registry.statuses.items():
            if isinstance(status, ModifyDamageStatus):
                modifier = DamageModifier(status.damage_type)
                damage_modifiers[status_id] = modifier
        return damage_modifiers

    def accumulate_damage_modifier(self, status_id, contribution):
        """
        Update the contribution amount in the modifier pool.
        """
        old_value = self.damage_modifiers[status_id].contribution
        new_value = old_value + contribution
        self.damage_modifiers[status_id].contribution = new_value

    def calculate_damage(self, damage_type, amount, logger) -> float:
        """
        Return net damage after applying modifiers.
        """
        net_contribution = 0
        for modifier in self.damage_modifiers.values():
            if modifier.matches(damage_type):
                net_contribution += modifier.contribution
                if modifier.contribution > 0:
                    logger.log(
                        f"Weakness to {damage_type} increased damage by {modifier.contribution:.0%}.",
                        True
                        )
                elif modifier.contribution < 0:
                    logger.log(
                        f"Resistance to {damage_type} decreased damage by {-modifier.contribution:.0%}.",
                        True
                        )
        amount = max(round((1 + net_contribution) * amount), 0)
        return amount

    # Cost modifiers

    def _initialize_cost_modifiers(self, status_registry) -> dict:
        """
        Populate the resource modifier pool with statuses.
        """
        cost_modifiers = {}
        for status_id, status in status_registry.statuses.items():
            if isinstance(status, ModifyCostStatus):
                modifier = CostModifier(status.affected_card_type)
                cost_modifiers[status_id] = modifier
        return cost_modifiers

    def accumulate_cost_modifier(self, status, contribution):
        """
        Accumulate contributions to cost modifiers in the pool.
        """
        old_value = self.cost_modifiers[status.status_id].contribution
        new_value = old_value + contribution
        self.cost_modifiers[status.status_id].contribution = new_value

    def clear_cost_modifiers(self, status, card_manager):
        """
        Clear contributions for a specific status.
        """
        if isinstance(status, ModifyCostStatus):
            self.cost_modifiers[status.status_id].contribution = 0
            card_type = status.affected_card_type
            self.recalculate_cost_modifiers(card_type, card_manager)

    def reset_cost_modifiers(self, card_type, card_manager):
        """
        Set cost modifiers affecting this card type to 0.
        """
        for card in card_manager.hand:
            if card.matches(card_type):
                card.reset_cost_modifier()

    def recalculate_cost_modifiers(self, card_type, card_manager):
        """
        Recalculate affected cost modifiers for affected cards.
        """
        self.reset_cost_modifiers(card_type, card_manager)
        for modifier in self.cost_modifiers.values():
            if modifier.matches(card_type):
                for card in card_manager.hand:
                    if card.matches(card_type):
                        self.modify_card_cost(card, modifier)

    def recalculate_all_costs(self, status_registry, card_manager):
        """
        Recalculate all cost modifiers for all cards.
        """
        for status_id in status_registry.list_statuses():
            status = status_registry.get_status(status_id)
            if isinstance(status, ModifyCostStatus):
                card_type = status.affected_card_type
                self.recalculate_cost_modifiers(card_type, card_manager)

    def modify_card_cost(self, card, modifier):
        """
        Change the cost of the given card.
        """
        card.change_cost_modifier(modifier.contribution)


# Modifier classes

class Modifier:
    """
    This is the base class representing a modifier that comes from an active
    status.
    """
    def __init__(self):
        """
        Initialize a new Modifier.
        """
        self.reset()

    def reset(self):
        """
        Reset this modifier's contribution to 0.
        """
        self.contribution = 0


class EffectModifier(Modifier):
    """
    This class represents a modifier that applies to all cards of a specified
    type and modifies the level of the specified effect on those cards.
    """
    def __init__(self, affected_card_type, affected_effect_id):
        """
        Initialize a new EffectModifier.
        """
        super().__init__()
        self.card_type = affected_card_type
        self.effect_id = affected_effect_id

    def matches(self, card_type, effect_id) -> bool:
        """
        Checks if the given card type and effect are subject to this modifier.
        """
        matches_type = self.card_type == card_type
        matches_effect = self.effect_id == effect_id
        return matches_type and matches_effect


class ResourceModifier(Modifier):
    """
    This class represents a modifier that changes the maximum value of a
    resource.
    """
    def __init__(self, resource_id):
        """
        Initialize a new ResourceModifier.
        """
        super().__init__()
        self.resource_id = resource_id

    def matches(self, resource_id) -> bool:
        """
        Checks if the given resource is subject to this modifier.
        """
        return self.resource_id == resource_id


class DamageModifier(Modifier):
    """
    This class represents a modifier that changes the amount of incoming damage
    based on its damage type.
    """
    def __init__(self, damage_type):
        """
        Initialize a new DamageModifier.
        """
        super().__init__()
        self.damage_type = damage_type

    def matches(self, damage_type):
        """
        Checks if the given damage type is subject to this modifier.
        """
        return damage_type == self.damage_type


class CostModifier(Modifier):
    """
    This class represents a modifier that changes the resource cost of a
    specific type of card.
    """
    def __init__(self, affected_card_type):
        """
        Initialize a new CostModifier.
        """
        super().__init__()
        self.affected_card_type = affected_card_type

    def matches(self, card_type):
        """
        Checks if the given card type (or subtype) is subject to this modifier.
        """
        return card_type == self.affected_card_type
