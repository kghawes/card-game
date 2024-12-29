from core.statuses import ModifyEffectStatus

class ModifierManager:
    def __init__(self, status_registry):
        self.effect_modifiers = self._initialize_effect_modifiers(status_registry)

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
        """Recalculate effect modifiers for affected cards."""
        self.reset_effect_modifiers(card_type, effect, card_manager)
        for modifier in self.effect_modifiers.values():
            if modifier.matches(card_type, effect):
                for card in card_manager.hand:
                    if card.matches(card_type):
                        self.modify_card_effect(card, effect, modifier)

    def recalculate_all_effects(self, status_registry, card_manager):
        """Recalculate effect modifiers for all cards."""
        for status_id in status_registry.list_statuses():
            status = status_registry.get_status(status_id)
            if isinstance(status, ModifyEffectStatus):
                card_type = status.affected_cards_enum
                effect = status.affected_effect
                self.recalculate_effect_modifiers(card_type, effect, card_manager)

    def modify_card_effect(self, card, effect, modifier):
        for effect_id, effect_level in card.effects.items():
            if effect in effect_id:
                amount = modifier.contribution
                effect_level.change_modifier(amount)

    def reset_card_effect(self, card, effect):
        for effect_id, effect_level in card.effects.items():
            if effect in effect_id:
                effect_level.reset_modifier()

class EffectModifier:
    def __init__(self, affected_card_type_enum, affected_effect_id):
        self.card_type_enum = affected_card_type_enum
        self.effect_id = affected_effect_id
        self.contribution = 0

    def matches(self, card_type_enum, effect_id) -> bool:
        matches_type = self.card_type_enum == card_type_enum
        matches_effect = self.effect_id == effect_id
        return matches_type and matches_effect
