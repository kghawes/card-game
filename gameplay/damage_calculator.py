"""
This module defines the DamageCalculator class.
"""
from math import floor
from utils.constants import DamageTypes as damage_types, StatusNames as status_names, \
    Attributes as attribute_names

class DamageCalculator:
    """
    Class responsible for calculating damage dealt from one combatant to another.
    """
    def calculate_damage(
            self, defender, attacker, amount, damage_type, registries
            ) -> int:
        """
        Calculate the final damage amount after applying statuses and attributes.
        """
        status_registry = registries.statuses
        attribute_registry = registries.attributes

        amount = self.process_hidden(defender, attacker, amount)

        amount = self.process_weakness_resist(defender, amount, damage_type)
        if amount <= 0:
            return 0

        if damage_type == damage_types.PHYSICAL.name:
            amount = self.process_defense(defender, amount, damage_type, status_registry)
            if amount <= 0:
                return 0
        else:
            amount = self.process_willpower(defender, amount, attribute_registry)
            if amount <= 0:
                return 0
            
            if attacker is not None and attacker != defender:
                amount = self.process_reflect(defender, attacker, amount, damage_type, status_registry)
                if amount <= 0:
                    return 0

                amount = self.process_spell_absorb(defender, attacker, amount, damage_type, status_registry)
                # TODO: consider changing to restore magicka instead of fortify intelligence
                if amount <= 0:
                    return 0
        
        return amount
    
    def process_willpower(self, defender, amount, attribute_registry) -> int:
        """
        Process willpower attribute for the defender.
        """
        willpower_level = defender.get_attribute_level(
            attribute_names.WILLPOWER.name
            )
        if willpower_level > 0:
            modifier = attribute_registry.get_attribute_modifier(attribute_names.WILLPOWER.name)
            reduction_percent = modifier * willpower_level
            reduced_amount = floor(amount * (1 - reduction_percent))
            difference = amount - reduced_amount
            if difference > 0:
                defender.event_manager.logger.log(
                    f"{defender.name}'s willpower reduced damage by {difference}!"
                    )
            amount = reduced_amount
            
        return amount

    def process_spell_absorb(self, defender, attacker, amount, damage_type, status_registry) -> int:
        """
        Process spell absorption status for the defender.
        """
        spell_absorb = defender.status_manager.get_leveled_status(status_names.SPELL_ABSORPTION.name)
        if spell_absorb is not None:
            spell_absorb_status = spell_absorb.reference
            spell_absorb_level = spell_absorb.get_level()
            amount, absorbed_amount = spell_absorb_status.calculate_block(
                    amount, damage_type, spell_absorb_level
                    )
            if absorbed_amount > 0:
                defender.event_manager.logger.log(
                        f"{defender.name} absorbed {absorbed_amount} damage from {attacker.name}!"
                        )
            defender.status_manager.change_status(
                    status_names.FORTIFY_INTELLIGENCE.name, absorbed_amount, defender, status_registry
                    )
                
        return amount

    def process_reflect(self, defender, attacker, amount, damage_type, status_registry) -> int:
        """
        Process reflect status for the defender.
        """
        reflect = defender.status_manager.get_leveled_status(status_names.REFLECT.name)
        if reflect is not None:
            reflect_status = reflect.reference
            reflect_level = reflect.get_level()
            amount, reflected_amount = reflect_status.calculate_block(
                    amount, damage_type, reflect_level
                    )
            if reflected_amount > 0:
                defender.event_manager.logger.log(
                        f"{defender.name} reflected {reflected_amount} damage back to {attacker.name}!"
                        )
                    
                # If attacker also has reflect, prevent infinite reflecting
            attacker_reflect = attacker.status_manager.get_leveled_status(
                    status_names.REFLECT.name
                    )
            will_damage_attacker = (
                    attacker_reflect is None 
                    or reflected_amount > attacker_reflect.get_level()
                )
            will_damage_defender = amount > 0
                # The reflection will go away if any portion of the damage is taken by either side
                # Otherwise, just stop reflection here
            if will_damage_attacker or will_damage_defender:
                attacker.take_damage(
                        defender, reflected_amount, damage_type, status_registry
                        )
                    
        return amount

    def process_defense(self, defender, amount, damage_type, status_registry) -> int:
        """
        Process defense status for the defender.
        """
        defense = defender.status_manager.get_leveled_status(status_names.DEFENSE.name)
        if defense is not None:
            defense_status = defense.reference
            defense_level = defense.get_level()
            old_amount = amount
            amount = defense_status.calculate_net_damage(
                defender, defense_level, amount, status_registry
                )
            if amount < old_amount:
                difference = old_amount - amount
                defender.event_manager.logger.log(
                    f"{defender.name}'s defense blocked {difference} damage!"
                        )
                        
        return amount

    def process_weakness_resist(self, defender, amount, damage_type) -> int:
        """
        Process weakness and resistance statuses for the defender.
        """
        old_amount = amount
        amount = defender.modifier_manager.calculate_damage(damage_type, amount, defender.event_manager.logger)
        if amount > old_amount:
            increase_percent = (amount - old_amount) / old_amount
            defender.event_manager.logger.log(
                f"The damage is super effective against {defender.name}! (+{increase_percent:.0%} damage)"
                )
        elif amount < old_amount:
            decrease_percent = (old_amount - amount) / old_amount
            defender.event_manager.logger.log(
                f"{defender.name} resists the damage! (-{decrease_percent:.0%} damage)"
                )
                
        return amount

    def process_hidden(self, defender, attacker, amount) -> int:
        """
        Process hidden status for the attacker.
        """
        if not attacker is None:
            hidden = attacker.status_manager.get_leveled_status(status_names.HIDDEN.name)
            if hidden is not None:
                hidden_level = hidden.get_level()
                hidden_status = hidden.reference
                mult = hidden_status.calculate_damage_multiplier(hidden_level)
                amount *= mult
                if mult > 1:
                    defender.event_manager.logger.log(
                        f"Critical strike! ({mult}x damage)"
                        )
                        
        return amount