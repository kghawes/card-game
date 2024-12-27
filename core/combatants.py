from gameplay.card_manager import CardManager
from gameplay.status_manager import StatusManager
from core.statuses import ModifyEffectStatus
from utils.constants import StatusNames, Resources, MIN_RESOURCE, SCALE_FACTOR

class Combatant:
    def __init__(
            self, name, max_health, max_stamina, max_magicka, starting_deck, 
            card_cache, status_registry
            ):
        self.name = name
        self.resources = {
            Resources.HEALTH.name: Resource(Resources.HEALTH, max_health),
            Resources.STAMINA.name: Resource(Resources.STAMINA, max_stamina),
            Resources.MAGICKA.name: Resource(Resources.MAGICKA, max_magicka)
        }
        self.card_manager = CardManager(starting_deck, card_cache)
        self.status_manager = StatusManager()
        self.modifier_pool = self._initialize_modifier_pool(status_registry)

    def _initialize_modifier_pool(self, status_registry) -> dict:
        """Populate the modifier pool with statuses and all 0 values."""
        modifier_pool = {} # Tracks accumulated contributions by status
        for status_id, status in status_registry.statuses.items():
            if isinstance(status, ModifyEffectStatus):
                card_type = status.affected_cards_enum
                effect = status.affected_effect
                modifier_pool[status_id] = {
                  "type": card_type,
                  "effect": effect,
                  "value": 0
                }
              
        return modifier_pool

    def accumulate_modifier_contribution(self, status, contribution):
        """Accumulate contributions to modifiers in the pool."""
        card_type = status.affected_cards_enum
        self.modifier_pool[status.status_id]["type"] = card_type
        self.modifier_pool[status.status_id]["effect"] = status.affected_effect
        old_value = self.modifier_pool[status.status_id]["value"]
        new_value = old_value + contribution
        self.modifier_pool[status.status_id]["value"] = new_value

    def clear_modifier_contributions(self, status):
        """Clear contributions for specific modifiers."""
        if isinstance(status, ModifyEffectStatus):
            self.modifier_pool[status.status_id]["value"] = 0
            card_type = status.affected_cards_enum
            effect = status.affected_effect
            self.recalculate_modifiers(card_type, effect)
        
    def reset_modifiers(self, card_type, effect):
        """Set all modifiers affecting this card type and effect to 0."""
        for card in self.card_manager.hand:
            if card.matches(card_type):
                for effect_id, effect_level in card.effects.items():
                    if effect in effect_id:
                        effect_level.reset_modifier()

    def recalculate_modifiers(self, card_type, effect):
        """Recalculate modifiers for affected cards."""
        self.reset_modifiers(card_type, effect)
        for modifier in self.modifier_pool.values():
            if modifier["type"] == card_type and modifier["effect"] == effect:
                for card in self.card_manager.hand:
                    if card.matches(card_type):
                        for effect_id, effect_level in card.effects.items():
                            if effect in effect_id:
                                effect_level.change_modifier(modifier["value"])
    
    def recalculate_all_modifiers(self, status_registry):
        """Recalculate modifiers for all cards."""
        for status_id in status_registry.list_statuses():
            status = status_registry.get_status(status_id)
            if isinstance(status, ModifyEffectStatus):
                self.recalculate_modifiers(
                    status.affected_cards_enum, status.affected_effect
                    )

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

    def take_damage(self, amount, damage_type_enum, status_registry):
        amount = self.calculate_damage(amount, damage_type_enum.name)
        defense = StatusNames.DEFENSE.name
        if self.status_manager.has_status(defense, self, status_registry):
            defense_status = status_registry.get_status(defense)
            defense_level = self.status_manager.get_status_level(defense)
            amount = defense_status.calculate_net_damage(
                self, defense_level, amount, status_registry
                )
        self.resources[Resources.HEALTH.name].change_value(-1 * amount)

    def calculate_damage(self, damage_amount, damage_type) -> int:
        """Apply resistances and weaknesses to incoming damage."""
        multiplier = 1
        for active_status_id, level in self.status_manager.statuses.items():
            sign_factor = 1
            if StatusNames.RESISTANCE.name in active_status_id:
                sign_factor = -1
            elif StatusNames.WEAKNESS.name not in active_status_id:
                continue
            if damage_type in active_status_id:
                multiplier += sign_factor * level * SCALE_FACTOR
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
        assert resource_id != Resources.HEALTH or amount >= 0
        self.resources[resource_id].change_value(amount)


class Resource:
    def __init__(self, resource_enum, max_value):
        self.resource_enum = resource_enum
        self.max_value = max_value
        self.modified_max_value = max_value
        self.current_value = max_value

    def change_value(self, amount):
        new_value = self.current_value + amount
        new_value = min(max(new_value, 0), self.modified_max_value)
        self.current_value = new_value

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
