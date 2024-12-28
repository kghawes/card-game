"""
This module defines the Combatant class and the helper Resource class.
"""
from gameplay.card_manager import CardManager
from gameplay.status_manager import StatusManager
from core.statuses import ModifyEffectStatus
import utils.constants as c

class Combatant:
    """Base class that represents an entity that can engage in combat,
    either the Player or an Enemy."""
    def __init__(
            self, name, max_health, max_stamina, max_magicka, starting_deck,
            card_cache, status_registry
            ):
        """Initialize a new Combatant."""
        self.name = name

        health_enum = c.Resources.HEALTH
        stamina_enum = c.Resources.STAMINA
        magicka_enum = c.Resources.MAGICKA
        self.resources = {
            health_enum.name: Resource(
                health_enum, max_health, c.HEALTH_STATUSES
                ),
            stamina_enum.name: Resource(
                stamina_enum, max_stamina, c.STAMINA_STATUSES
                ),
            magicka_enum.name: Resource(
                magicka_enum, max_magicka, c.MAGICKA_STATUSES
                )
        }

        self.card_manager = CardManager(starting_deck, card_cache)
        self.status_manager = StatusManager()
        self.modifier_pool = self._initialize_modifier_pool(status_registry)

    def _initialize_modifier_pool(self, status_registry) -> dict:
        """Populate the effect modifier pool with statuses and all 0 values."""
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
        """Accumulate contributions to effect modifiers in the pool."""
        card_type = status.affected_cards_enum
        self.modifier_pool[status.status_id]["type"] = card_type
        self.modifier_pool[status.status_id]["effect"] = status.affected_effect
        old_value = self.modifier_pool[status.status_id]["value"]
        new_value = old_value + contribution
        self.modifier_pool[status.status_id]["value"] = new_value

    def clear_modifier_contributions(self, status):
        """Clear contributions for specific effect modifiers."""
        if isinstance(status, ModifyEffectStatus):
            self.modifier_pool[status.status_id]["value"] = 0
            card_type = status.affected_cards_enum
            effect = status.affected_effect
            self.recalculate_modifiers(card_type, effect)

    def reset_modifiers(self, card_type, effect):
        """Set effect modifiers affecting this card type and effect to 0."""
        for card in self.card_manager.hand:
            if card.matches(card_type):
                for effect_id, effect_level in card.effects.items():
                    if effect in effect_id:
                        effect_level.reset_modifier()

    def recalculate_modifiers(self, card_type, effect):
        """Recalculate effect modifiers for affected cards."""
        self.reset_modifiers(card_type, effect)
        for modifier in self.modifier_pool.values():
            if modifier["type"] == card_type and modifier["effect"] == effect:
                for card in self.card_manager.hand:
                    if card.matches(card_type):
                        for effect_id, effect_level in card.effects.items():
                            if effect in effect_id:
                                effect_level.change_modifier(modifier["value"])

    def recalculate_all_modifiers(self, status_registry):
        """Recalculate effect modifiers for all cards."""
        for status_id in status_registry.list_statuses():
            status = status_registry.get_status(status_id)
            if isinstance(status, ModifyEffectStatus):
                card_type = status.affected_cards_enum
                effect = status.affected_effect
                self.recalculate_modifiers(card_type, effect)

    def get_health(self) -> int:
        """Get current health."""
        return self.resources[c.Resources.HEALTH.name].current_value

    def get_max_health(self) -> int:
        """Get maximum health."""
        return self.resources[c.Resources.HEALTH.name].get_max_value()

    def get_stamina(self) -> int:
        """Get current stamina."""
        return self.resources[c.Resources.STAMINA.name].current_value

    def get_max_stamina(self) -> int:
        """Get maximum stamina."""
        return self.resources[c.Resources.STAMINA.name].get_max_value()

    def get_magicka(self) -> int:
        """Get current magicka."""
        return self.resources[c.Resources.MAGICKA.name].current_value

    def get_max_magicka(self) -> int:
        """Get maximum magicka."""
        return self.resources[c.Resources.MAGICKA.name].get_max_value()

    def take_damage(self, amount, damage_type_enum, status_registry):
        """Accounting for statuses that modify incoming damage, change
        health to register damage taken."""
        amount = self.modify_damage(amount, damage_type_enum.name)
        defense = c.StatusNames.DEFENSE.name
        if self.status_manager.has_status(defense, self, status_registry):
            defense_status = status_registry.get_status(defense)
            defense_level = self.status_manager.get_status_level(defense)
            amount = defense_status.calculate_net_damage(
                self, defense_level, amount, status_registry
                )
        self.resources[c.Resources.HEALTH.name].change_value(-1 * amount)

    def modify_damage(self, damage_amount, damage_type) -> int:
        """Apply resistances and weaknesses to incoming damage."""
        multiplier = 1
        for active_status_id, level in self.status_manager.statuses.items():
            sign_factor = 1
            if c.StatusNames.RESISTANCE.name in active_status_id:
                sign_factor = -1
            elif c.StatusNames.WEAKNESS.name not in active_status_id:
                continue
            if damage_type in active_status_id:
                multiplier += sign_factor * level * c.SCALE_FACTOR
        return round(damage_amount * multiplier)

    def is_alive(self) -> bool:
        """Check if the Combatant has more than zero health."""
        return self.get_health() > 0

    def replenish_resources_for_turn(self):
        """Reset current stamina and magicka to their maximum values."""
        self.resources[c.Resources.STAMINA.name].replenish()
        self.resources[c.Resources.MAGICKA.name].replenish()

    def reset_for_turn(self):
        """Reset values for the new turn."""
        self.card_manager.reset_cards_to_draw()
        self.replenish_resources_for_turn()

    def change_resource(self, resource_id, amount):
        """Change the value of a given resource by a given amount."""
        assert resource_id != c.Resources.HEALTH or amount >= 0
        self.resources[resource_id].change_value(amount)


class Resource:
    """Represents health, stamina, or magicka."""
    def __init__(self, resource_enum, max_value, modifying_statuses):
        """Initialize a new Resource."""
        self.resource_enum = resource_enum
        self.max_value = max_value
        self.current_value = max_value
        self.modifier_contributions = {}
        for status_id in modifying_statuses:
            self.modifier_contributions[status_id] = 0

    def change_value(self, amount):
        """Change the current value by the given amount."""
        new_value = self.current_value + amount
        new_value = min(max(new_value, 0), self.get_max_value())
        self.current_value = new_value

    def try_spend(self, amount) -> bool:
        """Reduce the current value by the given amount or return false
        if there isn't enough."""
        if self.current_value < amount:
            return False
        self.current_value = self.current_value - amount
        return True

    def reset_max_value(self):
        """Clear all modifiers and reset maximum value to its base value."""
        for status_id in self.modifier_contributions:
            self.modifier_contributions[status_id] = 0

    def get_max_value(self) -> int:
        """Get the maximum value of the resource."""
        net_contribution = 0
        for contribution in self.modifier_contributions.values():
            net_contribution += contribution
        return max(self.max_value + net_contribution, c.MIN_RESOURCE)

    def modify_max_value(self, status_id, amount):
        """Change the maximum value by the given amount."""
        if status_id in self.modifier_contributions:
            old_value = self.modifier_contributions[status_id]
            new_value = old_value + amount
            self.modifier_contributions[status_id] = new_value
        self.current_value = min(self.current_value, self.get_max_value())

    def replenish(self):
        """Reset the current value to the maximum value."""
        self.current_value = self.get_max_value()
