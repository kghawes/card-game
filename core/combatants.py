"""
This module defines the Combatant class.
"""
from gameplay.card_manager import CardManager
from gameplay.status_manager import StatusManager
from gameplay.modifier_manager import ModifierManager
from core.resources import Resource
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
        self.modifier_manager = ModifierManager(status_registry)

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
