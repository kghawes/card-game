"""
This module defined the ModifierManager class and modifier classes.
"""
from core.statuses import ModifyEffectStatus

class ModifierManager:
    """This class holds the details of currently active status
    modifications and controls their update and application."""
    def __init__(self, status_registry):
        """Initialize a new ModifierManager."""
        self.effect_modifiers = self._initialize_effect_modifiers(
            status_registry
            )

    def _initialize_effect_modifiers(self, status_registry) -> dict:
        """Populate the effect modifier pool with statuses."""
        effect_modifiers = {} # Tracks accumulated contributions by status
        for status_id, status in status_registry.statuses.items():
            if isinstance(status, ModifyEffectStatus):
                card_type = status.affected_cards_enum
                effect = status.affected_effect
                effect_modifiers[status_id] = EffectModifier(card_type, effect)
        return effect_modifiers

    def accumulate_effect_modifier(self, status, contribution):
        """Accumulate contributions to effect modifiers in the pool."""
        old_value = self.effect_modifiers[status.status_id].contribution
        new_value = old_value + contribution
        self.effect_modifiers[status.status_id].contribution = new_value

    def clear_effect_modifiers(self, status, card_manager):
        """Clear contributions for specific effect modifiers."""
        if isinstance(status, ModifyEffectStatus):
            self.effect_modifiers[status.status_id].contribution = 0
            card_type = status.affected_cards_enum
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
                card_type = status.affected_cards_enum
                effect = status.affected_effect
                self.recalculate_effect_modifiers(
                    card_type, effect, card_manager
                    )

    def modify_card_effect(self, card, effect, modifier):
        """Change the effect level of the given effect on this card."""
        for effect_id, effect_level in card.effects.items():
            if effect in effect_id:
                amount = modifier.contribution
                effect_level.change_modifier(amount)

    def reset_card_effect(self, card, effect):
        """Reset the effect level of the given effect on this card."""
        for effect_id, effect_level in card.effects.items():
            if effect in effect_id:
                effect_level.reset_modifier()

class EffectModifier:
    """This class represents a modifier that applies to all cards of a
    specified type and modifies the level of the specified effect on
    those cards."""
    def __init__(self, affected_card_type_enum, affected_effect_id):
        """Initialize a new EffectModifier."""
        self.card_type_enum = affected_card_type_enum
        self.effect_id = affected_effect_id
        self.contribution = 0

    def matches(self, card_type_enum, effect_id) -> bool:
        """Checks if the given card type and effect are subject to
        this modifier."""
        matches_type = self.card_type_enum == card_type_enum
        matches_effect = self.effect_id == effect_id
        return matches_type and matches_effect
