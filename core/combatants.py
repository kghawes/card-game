"""
This module defines the Combatant class.
"""
from gameplay.card_manager import CardManager
from gameplay.status_manager import StatusManager
from gameplay.modifier_manager import ModifierManager
from gameplay.damage_calculator import DamageCalculator
from core.resources import Resource
from utils.constants import Resources as Res, Attributes
from utils.formatter import Formatter

class Combatant:
    """
    Base class that represents an entity that can engage in combat, either the
    Player or an Enemy.
    """
    def __init__(
            self, name, max_health, max_stamina, max_magicka, starting_deck,
            registries, is_enemy, event_manager, starting_attributes=None
            ):
        """
        Initialize a new Combatant.
        """
        self.name = name
        self.is_enemy = is_enemy
        health_id = Res.HEALTH.name
        stamina_id = Res.STAMINA.name
        magicka_id = Res.MAGICKA.name
        self.resources = {
            health_id: Resource(health_id, max_health),
            stamina_id: Resource(stamina_id, max_stamina),
            magicka_id: Resource(magicka_id, max_magicka)
        }
        self.card_manager = CardManager(
            starting_deck, registries.cards, event_manager, registries.effects
            )
        self.status_manager = StatusManager(event_manager)
        self.modifier_manager = ModifierManager(registries.statuses)
        self.cards_played_this_turn = 0
        self.event_manager = event_manager
        self.formatter = Formatter()
        self.damage_calculator = DamageCalculator()
        # Initialize self.attributes and self.attribute_deltas
        self.initialize_attributes(starting_attributes)

    def initialize_attributes(self, initial_values=None):
        """
        Setup character attributes.
        """
        self.attributes = {}
        self.attribute_deltas = {}
        for attribute in Attributes:
            self.attribute_deltas[attribute.name] = 0
            if initial_values and attribute.name in initial_values:
                self.attributes[attribute.name] = initial_values[attribute.name]
            else:
                self.attributes[attribute.name] = 0
    
    def reset_attribute_deltas(self):
        """
        Reset attribute deltas to zero.
        """
        for attribute in Attributes:
            self.attribute_deltas[attribute.name] = 0

    def get_combatant_data(self) -> dict:
        """
        Get the data to display in the UI.
        """
        statuses = {}
        for status_id, leveled_status in self.status_manager.statuses.items():
            status = leveled_status.reference
            level = leveled_status.get_level()
            statuses[status_id] = {
                'name': leveled_status.name,
                'level': level,
                'description': self.formatter.format_status_data(
                    status, level, is_player=not self.is_enemy
                    )
            }
        attributes = {}
        for attribute_id, value in self.attributes.items():
            attributes[attribute_id] = value + self.attribute_deltas[attribute_id]
        return {
            'name': self.name,
            'health': self.get_health(),
            'max_health': self.get_max_health(),
            'stamina': self.get_stamina(),
            'max_stamina': self.get_max_stamina(),
            'magicka': self.get_magicka(),
            'max_magicka': self.get_max_magicka(),
            'statuses': statuses,
            'attributes': attributes
        }

    def get_health(self) -> int:
        """
        Get current health.
        """
        return self.resources[Res.HEALTH.name].current

    def get_max_health(self) -> int:
        """
        Get maximum health, including modifiers.
        """
        return self.resources[Res.HEALTH.name].get_max(self.modifier_manager)

    def get_stamina(self) -> int:
        """
        Get current stamina.
        """
        return self.resources[Res.STAMINA.name].current

    def get_max_stamina(self) -> int:
        """
        Get maximum stamina, including modifiers.
        """
        return self.resources[Res.STAMINA.name].get_max(self.modifier_manager)

    def get_magicka(self) -> int:
        """
        Get current magicka.
        """
        return self.resources[Res.MAGICKA.name].current

    def get_max_magicka(self) -> int:
        """
        Get maximum magicka, including modifiers.
        """
        return self.resources[Res.MAGICKA.name].get_max(self.modifier_manager)

    def get_attribute_level(self, attribute_id) -> int:
        """
        Get the level of a character attribute, including deltas.
        """
        base_level = self.attributes.get(attribute_id, 0)
        delta = self.attribute_deltas.get(attribute_id, 0)
        return base_level + delta

    def take_damage(self, attacker, amount, damage_type, registries):
        """
        Accounting for statuses that modify incoming damage, change health to
        register damage taken.
        """
        if amount <= 0:
            return

        amount = self.damage_calculator.calculate_damage(
                self, attacker, amount, damage_type, registries
                )

        health = self.resources[Res.HEALTH.name]
        health.change_value(-amount, self.modifier_manager)
        self.event_manager.logger.log(
            f"{self.name} took {amount} damage!"
            )

    def is_alive(self) -> bool:
        """
        Check if the Combatant has more than zero health.
        """
        return self.get_health() > 0

    def replenish_resources_for_turn(self):
        """
        Reset current stamina and magicka to their maximum values.
        """
        stamina = self.resources[Res.STAMINA.name]
        stamina.replenish(self.modifier_manager)
        magicka = self.resources[Res.MAGICKA.name]
        magicka.replenish(self.modifier_manager)

    def reset_for_turn(self):
        """
        Reset values for the new turn.
        """
        self.replenish_resources_for_turn()
        self.cards_played_this_turn = 0

    def change_resource(self, resource_id, amount):
        """
        Change the value of a given resource by a given amount.
        """
        self.resources[resource_id].change_value(
            amount, self.modifier_manager
            )
