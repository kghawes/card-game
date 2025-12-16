"""
This module defines the Combatant class.
"""
from gameplay.card_manager import CardManager
from gameplay.status_manager import StatusManager
from gameplay.modifier_manager import ModifierManager
from core.resources import Resource
from utils.constants import Resources as r, \
    StatusNames as s, DamageTypes as d, Attributes as a
from utils.formatter import Formatter

class Combatant:
    """
    Base class that represents an entity that can engage in combat, either the
    Player or an Enemy.
    """
    def __init__(
            self, name, max_health, max_stamina, max_magicka, starting_deck,
            card_cache, registries, is_enemy, event_manager, starting_attributes=None
            ):
        """
        Initialize a new Combatant.
        """
        self.name = name
        self.is_enemy = is_enemy
        health_id = r.HEALTH.name
        stamina_id = r.STAMINA.name
        magicka_id = r.MAGICKA.name
        self.resources = {
            health_id: Resource(health_id, max_health),
            stamina_id: Resource(stamina_id, max_stamina),
            magicka_id: Resource(magicka_id, max_magicka)
        }
        self.card_manager = CardManager(starting_deck, card_cache, event_manager, registries.effects)
        self.status_manager = StatusManager(event_manager)
        self.modifier_manager = ModifierManager(registries.statuses)
        self.cards_played_this_turn = 0
        self.event_manager = event_manager
        self.formatter = Formatter()
        self.initialize_attributes(starting_attributes)

    def initialize_attributes(self, initial_values=None):
        """
        Setup character attributes.
        """
        self.attributes = {}
        for attribute in a:
            if initial_values and attribute.name in initial_values:
                self.attributes[attribute.name] = initial_values[attribute.name]
            else:
                self.attributes[attribute.name] = 0

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
                'description': self.formatter.format_status_data(status, level, is_player=not self.is_enemy)
            }
        return {
            'name': self.name,
            'health': self.get_health(),
            'max_health': self.get_max_health(),
            'stamina': self.get_stamina(),
            'max_stamina': self.get_max_stamina(),
            'magicka': self.get_magicka(),
            'max_magicka': self.get_max_magicka(),
            'statuses': statuses
        }

    def get_health(self) -> int:
        """
        Get current health.
        """
        return self.resources[r.HEALTH.name].current

    def get_max_health(self) -> int:
        """
        Get maximum health.
        """
        return self.resources[r.HEALTH.name].get_max(self.modifier_manager)

    def get_stamina(self) -> int:
        """
        Get current stamina.
        """
        return self.resources[r.STAMINA.name].current

    def get_max_stamina(self) -> int:
        """
        Get maximum stamina.
        """
        return self.resources[r.STAMINA.name].get_max(self.modifier_manager)

    def get_magicka(self) -> int:
        """
        Get current magicka.
        """
        return self.resources[r.MAGICKA.name].current

    def get_max_magicka(self) -> int:
        """
        Get maximum magicka.
        """
        return self.resources[r.MAGICKA.name].get_max(self.modifier_manager)

    def take_damage(self, attacker, amount, damage_type, status_registry):
        """
        Accounting for statuses that modify incoming damage, change health to
        register damage taken.
        """
        if amount <= 0:
            return

        if not attacker is None:
            hidden = attacker.status_manager.get_leveled_status(s.HIDDEN.name)
            if hidden is not None:
                hidden_level = hidden.get_level()
                hidden_status = hidden.reference
                mult = hidden_status.calculate_damage_multiplier(hidden_level)
                amount *= mult
                if mult > 1:
                    self.event_manager.logger.log(
                        f"Critical strike! ({mult}x damage)"
                        )

        old_amount = amount
        amount = self.modifier_manager.calculate_damage(damage_type, amount, self.event_manager.logger)
        if amount > old_amount:
            increase_percent = (amount - old_amount) / old_amount
            self.event_manager.logger.log(
                f"The damage is super effective against {self.name}! (+{increase_percent:.0%} damage)"
                )
        elif amount < old_amount:
            decrease_percent = (old_amount - amount) / old_amount
            self.event_manager.logger.log(
                f"{self.name} resists the damage! (-{decrease_percent:.0%} damage)"
                )

        if amount <= 0:
            return

        if damage_type == d.PHYSICAL.name:
            defense = self.status_manager.get_leveled_status(s.DEFENSE.name)
            if defense is not None:
                defense_status = defense.reference
                defense_level = defense.get_level()
                old_amount = amount
                amount = defense_status.calculate_net_damage(
                    self, defense_level, amount, status_registry
                    )
                if amount < old_amount:
                    difference = old_amount - amount
                    self.event_manager.logger.log(
                        f"{self.name}'s defense blocked {difference} damage!"
                        )
                if amount <= 0:
                    return
        elif not attacker is None and attacker != self:
            reflect = self.status_manager.get_leveled_status(s.REFLECT.name)
            if reflect is not None:
                reflect_status = reflect.reference
                reflect_level = reflect.get_level()
                amount, reflected_amount = reflect_status.calculate_block(
                    amount, damage_type, reflect_level
                    )
                if reflected_amount > 0:
                    self.event_manager.logger.log(
                        f"{self.name} reflected {reflected_amount} damage back to {attacker.name}!"
                        )
                    
                # If attacker also has reflect, prevent infinite reflecting
                attacker_reflect = attacker.status_manager.get_leveled_status(
                    s.REFLECT.name
                    )
                if amount == 0 and attacker_reflect is not None:
                    if reflected_amount <= attacker_reflect.get_level():
                        return
                
                attacker.take_damage(
                    self, reflected_amount, damage_type, status_registry
                    )
                if amount <= 0:
                    return

            spell_absorb = self.status_manager.get_leveled_status(s.SPELL_ABSORPTION.name)
            if spell_absorb is not None:
                spell_absorb_status = spell_absorb.reference
                spell_absorb_level = spell_absorb.get_level()
                amount, absorbed_amount = spell_absorb_status.calculate_block(
                    amount, damage_type, spell_absorb_level
                    )
                if absorbed_amount > 0:
                    self.event_manager.logger.log(
                        f"{self.name} absorbed {absorbed_amount} damage from {attacker.name}!"
                        )
                self.status_manager.change_status(
                    s.FORTIFY_INTELLIGENCE.name, absorbed_amount, self, status_registry
                    )
                if amount <= 0:
                    return

        health = self.resources[r.HEALTH.name]
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
        stamina = self.resources[r.STAMINA.name]
        stamina.replenish(self.modifier_manager)
        magicka = self.resources[r.MAGICKA.name]
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
