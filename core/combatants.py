"""
This module defines the Combatant class.
"""
from gameplay.card_manager import CardManager
from gameplay.status_manager import StatusManager
from gameplay.modifier_manager import ModifierManager
from core.resources import Resource
from utils.constants import Resources as r, StatusNames as s, SCALE_FACTOR

class Combatant:
    """Base class that represents an entity that can engage in combat,
    either the Player or an Enemy."""
    def __init__(
            self, name, max_health, max_stamina, max_magicka, starting_deck,
            card_cache, status_registry
            ):
        """Initialize a new Combatant."""
        self.name = name

        health_enum = r.HEALTH
        stamina_enum = r.STAMINA
        magicka_enum = r.MAGICKA
        self.resources = {
            health_enum: Resource(health_enum, max_health),
            stamina_enum: Resource(stamina_enum, max_stamina),
            magicka_enum: Resource(magicka_enum, max_magicka)
        }

        self.card_manager = CardManager(starting_deck, card_cache)
        self.status_manager = StatusManager()
        self.modifier_manager = ModifierManager(status_registry)

    def get_health(self) -> int:
        """Get current health."""
        return self.resources[r.HEALTH].current_value

    def get_max_health(self) -> int:
        """Get maximum health."""
        return self.resources[r.HEALTH].get_max_value(self.modifier_manager)

    def get_stamina(self) -> int:
        """Get current stamina."""
        return self.resources[r.STAMINA].current_value

    def get_max_stamina(self) -> int:
        """Get maximum stamina."""
        return self.resources[r.STAMINA].get_max_value(self.modifier_manager)

    def get_magicka(self) -> int:
        """Get current magicka."""
        return self.resources[r.MAGICKA].current_value

    def get_max_magicka(self) -> int:
        """Get maximum magicka."""
        return self.resources[r.MAGICKA].get_max_value(self.modifier_manager)

    def take_damage(self, amount, damage_type_enum, status_registry):
        """Accounting for statuses that modify incoming damage, change
        health to register damage taken."""
        amount = self.modify_damage(amount, damage_type_enum.name)
        defense = s.DEFENSE.name
        if self.status_manager.has_status(defense, self, status_registry):
            defense_status = status_registry.get_status(defense)
            defense_level = self.status_manager.get_status_level(defense)
            amount = defense_status.calculate_net_damage(
                self, defense_level, amount, status_registry
                )
        self.resources[r.HEALTH].change_value(-amount, self.modifier_manager)

#move to modifier manager
    def modify_damage(self, damage_amount, damage_type) -> int:
        """Apply resistances and weaknesses to incoming damage."""
        multiplier = 1
        for active_status_id, level in self.status_manager.statuses.items():
            sign_factor = 1
            if s.RESISTANCE.name in active_status_id:
                sign_factor = -1
            elif s.WEAKNESS.name not in active_status_id:
                continue
            if damage_type in active_status_id:
                multiplier += sign_factor * level * SCALE_FACTOR
        return round(damage_amount * multiplier)

    def is_alive(self) -> bool:
        """Check if the Combatant has more than zero health."""
        return self.get_health() > 0

    def replenish_resources_for_turn(self):
        """Reset current stamina and magicka to their maximum values."""
        stamina = self.resources[r.STAMINA]
        stamina.replenish(self.modifier_manager)
        magicka = self.resources[r.MAGICKA]
        magicka.replenish(self.modifier_manager)

    def reset_for_turn(self):
        """Reset values for the new turn."""
        self.card_manager.reset_cards_to_draw()
        self.replenish_resources_for_turn()

    def change_resource(self, resource_enum, amount):
        """Change the value of a given resource by a given amount."""
        assert resource_enum != r.HEALTH or amount >= 0
        self.resources[resource_enum].change_value(
            amount, self.modifier_manager
            )
