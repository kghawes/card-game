"""
This module defines the Combatant class.
"""
from gameplay.card_manager import CardManager
from gameplay.status_manager import StatusManager
from gameplay.modifier_manager import ModifierManager
from core.resources import Resource
from utils.constants import Resources as r, StatusNames as s, DamageTypes as d

class Combatant:
    """
    Base class that represents an entity that can engage in combat, either the
    Player or an Enemy.
    """
    def __init__(
            self, name, max_health, max_stamina, max_magicka, starting_deck,
            card_cache, status_registry, is_enemy, event_manager
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
        self.card_manager = CardManager(starting_deck, card_cache, event_manager)
        self.status_manager = StatusManager()
        self.modifier_manager = ModifierManager(status_registry)
        self.cards_played_this_turn = 0
        self.event_manager = event_manager

    def get_combatant_data(self):
        """
        Get the data to display in the UI.
        """
        return {
            'name': self.name,
            'health': self.get_health(),
            'max_health': self.get_max_health(),
            'stamina': self.get_stamina(),
            'max_stamina': self.get_max_stamina(),
            'magicka': self.get_magicka(),
            'max_magicka': self.get_max_magicka(),
            'statuses': dict(self.status_manager.statuses)
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

        hidden = s.HIDDEN.name
        if attacker.status_manager.has_status(
                hidden, attacker, status_registry
                ):
            hidden_level = attacker.status_manager.get_status_level(hidden)
            hidden_status = status_registry.get_status(hidden)
            mult = hidden_status.calculate_damage_multiplier(hidden_level)
            amount *= mult
            if mult > 1:
                self.event_manager.logger.log(
                    f"{attacker.name} took {self.name} by surprise! Critical strike! ({mult}x damage)"
                    )

        old_amount = amount
        amount = self.modifier_manager.calculate_damage(damage_type, amount, self.event_manager.logger)
        if amount > old_amount:
            increase = (amount - old_amount) / old_amount
            self.event_manager.logger.log(
                f"The attack is super effective against {self.name}! (+{increase:.0%} damage)"
                )
        elif amount < old_amount:
            decrease = (old_amount - amount) / old_amount
            self.event_manager.logger.log(
                f"{self.name} resists the attack! (-{decrease:.0%} damage)"
                )

        if amount <= 0:
            return

        if damage_type == d.PHYSICAL.name:
            defense = s.DEFENSE.name
            if self.status_manager.has_status(defense, self, status_registry):
                defense_status = status_registry.get_status(defense)
                defense_level = self.status_manager.get_status_level(defense)
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
        elif attacker != self:
            reflect = s.REFLECT.name
            if self.status_manager.has_status(reflect, self, status_registry):
                reflect_status = status_registry.get_status(reflect)
                reflect_level = self.status_manager.get_status_level(reflect)
                amount, reflected_amount = reflect_status.calculate_block(
                    amount, damage_type, reflect_level
                    )
                if reflected_amount > 0:
                    self.event_manager.logger.log(
                        f"{self.name} reflected {reflected_amount} damage back to {attacker.name}!"
                        )
                if amount == 0 and attacker.status_manager.has_status(
                        reflect, attacker, status_registry
                        ):
                    attacker_reflect_level = attacker.status_manager.get_status_level(
                        reflect
                        )
                    if reflected_amount <= attacker_reflect_level:
                        return # Prevent infinite reflecting back and forth
                attacker.take_damage(
                    self, reflected_amount, damage_type, status_registry
                    )
                if amount <= 0:
                    return

            spell_absorb = s.SPELL_ABSORPTION.name
            if self.status_manager.has_status(
                    spell_absorb, self, status_registry
                    ):
                absorb_status = status_registry.get_status(spell_absorb)
                absorb_level = self.status_manager.get_status_level(
                    spell_absorb
                    )
                amount, absorbed_amount = absorb_status.calculate_block(
                    amount, damage_type, absorb_level
                    )
                if absorbed_amount > 0:
                    self.event_manager.logger.log(
                        f"{self.name} absorbed {absorbed_amount} damage from {attacker.name}!"
                        )
                fortify_int = s.FORTIFY_INTELLIGENCE.name
                self.status_manager.change_status(
                    fortify_int, absorbed_amount, self, status_registry
                    )

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
