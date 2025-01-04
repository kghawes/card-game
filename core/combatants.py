"""
This module defines the Combatant class.
"""
from gameplay.card_manager import CardManager
from gameplay.status_manager import StatusManager
from gameplay.modifier_manager import ModifierManager
from core.resources import Resource
from utils.constants import Resources as r, StatusNames as s

class Combatant:
    """Base class that represents an entity that can engage in combat,
    either the Player or an Enemy."""
    def __init__(
            self, name, max_health, max_stamina, max_magicka, starting_deck,
            card_cache, status_registry
            ):
        """Initialize a new Combatant."""
        self.name = name

        health_id = r.HEALTH.name
        stamina_id = r.STAMINA.name
        magicka_id = r.MAGICKA.name
        self.resources = {
            health_id: Resource(health_id, max_health),
            stamina_id: Resource(stamina_id, max_stamina),
            magicka_id: Resource(magicka_id, max_magicka)
        }

        self.card_manager = CardManager(starting_deck, card_cache)
        self.status_manager = StatusManager()
        self.modifier_manager = ModifierManager(status_registry)

    def get_health(self) -> int:
        """Get current health."""
        return self.resources[r.HEALTH.name].current

    def get_max_health(self) -> int:
        """Get maximum health."""
        return self.resources[r.HEALTH.name].get_max(self.modifier_manager)

    def get_stamina(self) -> int:
        """Get current stamina."""
        return self.resources[r.STAMINA.name].current

    def get_max_stamina(self) -> int:
        """Get maximum stamina."""
        return self.resources[r.STAMINA.name].get_max(self.modifier_manager)

    def get_magicka(self) -> int:
        """Get current magicka."""
        return self.resources[r.MAGICKA.name].current

    def get_max_magicka(self) -> int:
        """Get maximum magicka."""
        return self.resources[r.MAGICKA.name].get_max(self.modifier_manager)

    def take_damage(self, amount, damage_type, status_registry):
        """Accounting for statuses that modify incoming damage, change
        health to register damage taken."""
        amount = self.modifier_manager.calculate_damage(damage_type, amount)
        defense = s.DEFENSE.name
        if self.status_manager.has_status(defense, self, status_registry):
            defense_status = status_registry.get_status(defense)
            defense_level = self.status_manager.get_status_level(defense)
            amount = defense_status.calculate_net_damage(
                self, defense_level, amount, status_registry
                )
        health = self.resources[r.HEALTH.name]
        health.change_value(-amount, self.modifier_manager)

    def is_alive(self) -> bool:
        """Check if the Combatant has more than zero health."""
        return self.get_health() > 0

    def replenish_resources_for_turn(self):
        """Reset current stamina and magicka to their maximum values."""
        stamina = self.resources[r.STAMINA.name]
        stamina.replenish(self.modifier_manager)
        magicka = self.resources[r.MAGICKA.name]
        magicka.replenish(self.modifier_manager)

    def reset_for_turn(self):
        """Reset values for the new turn."""
        self.replenish_resources_for_turn()

    def change_resource(self, resource_id, amount):
        """Change the value of a given resource by a given amount."""
        assert resource_id != r.HEALTH.name or amount >= 0
        self.resources[resource_id].change_value(amount, self.modifier_manager)
