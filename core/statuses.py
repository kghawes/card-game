"""
This module defines the Status class, its child classes, and the
StatusRegistry.
"""
import random
import utils.constants as c
from utils.utils import load_json

class Status:
    """
    The base class for an ongoing status effect.
    """
    def __init__(self, status_id, description, applies_immediately):
        """
        Initialize a new Status.
        """
        self.status_id = status_id
        self.name = c.StatusNames[status_id].value
        self.description = description
        self.applies_immediately = applies_immediately

    def modify_value(self, old_value, amount, is_reduction, min_result) -> int:
        """
        Change a given value by a given amount.
        """
        if is_reduction:
            return max(old_value - amount, min_result)
        return old_value + amount

    def trigger_on_turn(self, subject, level, status_registry=None):
        """
        Base method for polymorphism. Activate the status effect at the
        beginning of the turn.
        """
        return

    def trigger_on_change(self, subject, level):
        """
        Base method for polymorphism. Activate the status effect when its level
        is changed in order to recalculate.
        """
        return

    def expire(self, subject, logger):
        """
        Base method for polymorphism. Clean up the status effects when the
        Status goes away and log the expiration.
        """
        logger.log(
            f"{self.name} expires."
            )


class ModifyEffectStatus(Status):
    """
    Statuses that change the levels of effects on cards.
    """
    def __init__(
            self, status_id, description, affected_card_type, affected_effect,
            sign_factor
            ):
        """
        Initialize a new ModifyEffectStatus.
        """
        super().__init__(status_id, description, applies_immediately=True)
        self.affected_card_type = affected_card_type
        self.affected_effect = affected_effect
        self.sign_factor = sign_factor

    def trigger_on_turn(self, subject, level, status_registry):
        """
        Recalculate effects at the start of each turn.
        """
        card_type = self.affected_card_type
        effect = self.affected_effect
        subject.modifier_manager.recalculate_effect_modifiers(
            card_type, effect, subject.card_manager
            )

    def trigger_on_change(self, subject, level):
        """
        Accumulate contributions to the modifier pool when level changes.
        """
        contribution = self.sign_factor * level
        subject.modifier_manager.accumulate_effect_modifier(self, contribution)
        card_type = self.affected_card_type
        effect = self.affected_effect
        subject.modifier_manager.recalculate_effect_modifiers(
            card_type, effect, subject.card_manager
            )

    def expire(self, subject, logger):
        """
        Clear contributions when the status expires.
        """
        super().expire(subject, logger)
        subject.modifier_manager.clear_effect_modifiers(
            self, subject.card_manager
            )


class ModifyCostStatus(Status):
    """
    Statuses that change the stamina or magicka cost on cards.
    """
    def __init__(
            self, status_id, description, affected_card_type, sign_factor
            ):
        """
        Initialize a new ModifyCostStatus.
        """
        super().__init__(status_id, description, applies_immediately=True)
        self.affected_card_type = affected_card_type
        self.sign_factor = sign_factor

    def trigger_on_turn(self, subject, level, status_registry):
        """
        Recalculate costs at the start of each turn.
        """
        card_type = self.affected_card_type
        subject.modifier_manager.recalculate_cost_modifiers(
            card_type, subject.card_manager
            )

    def trigger_on_change(self, subject, level):
        """
        Accumulate contributions to the modifier pool when level changes.
        """
        contribution = self.sign_factor * level
        subject.modifier_manager.accumulate_cost_modifier(self, contribution)
        card_type = self.affected_card_type
        subject.modifier_manager.recalculate_cost_modifiers(
            card_type, subject.card_manager
            )

    def expire(self, subject, logger):
        """
        Clear contributions when the status expires.
        """
        super().expire(subject, logger)
        subject.modifier_manager.clear_cost_modifiers(
            self, subject.card_manager
            )


class ModifyMaxResourceStatus(Status):
    """
    Statuses that change maximum stamina or magicka.
    """
    def __init__(self, status_id, description, resource_id, sign_factor):
        """
        Initialize a new ModifyMaxResourceStatus.
        """
        super().__init__(status_id, description, applies_immediately=True)
        self.resource_id = resource_id
        self.sign_factor = sign_factor

    def trigger_on_change(self, subject, level):
        modifier_manager = subject.modifier_manager
        amount = level * self.sign_factor
        modifier_manager.modify_max_resource(
            subject.resources[self.resource_id], self.status_id, amount
            )


class ModifyDrawStatus(Status):
    """
    Statuses that affect the number of cards drawn per turn.
    """
    def __init__(self, status_id, description, sign_factor):
        """
        Initialize a new ModifyDrawStatus
        """
        super().__init__(status_id, description, applies_immediately=True)
        self.sign_factor = sign_factor

    def trigger_on_change(self, subject, level):
        """
        Update the modifier pool with the new contribution.
        """
        modifier_manager = subject.modifier_manager
        amount = level * self.sign_factor
        modifier_manager.modify_cards_to_draw(self.status_id, amount)


class ModifyDamageStatus(Status):
    """
    Stasuses that affect the amount of damage taken.
    """
    def __init__(self, status_id, description, damage_type, sign_factor):
        """
        Initialize a new ModifyDamageStatus.
        """
        super().__init__(status_id, description, applies_immediately=True)
        self.damage_type = damage_type
        self.sign_factor = sign_factor

    def trigger_on_change(self, subject, level):
        """
        Update the modifier pool with the new contribution factor.
        Does not factor in the multiplier for the specific status.
        """
        modifier_manager = subject.modifier_manager
        amount = level * self.sign_factor
        modifier_manager.accumulate_damage_modifier(self.status_id, amount)


class ModifyAttributeStatus(Status):
    """
    Statuses that affect combatant attribute values.
    """
    def __init__(self, status_id, description, sign_factor, attribute_id):
        """
        Initialize a new ModifyAttributeStatus
        """
        super().__init__(status_id, description, applies_immediately=True)
        self.sign_factor = sign_factor
        self.attribute_id = attribute_id

    def trigger_on_change(self, subject, change):
        """
        Update the subject's attribute delta.
        """
        subject.attribute_deltas[self.attribute_id] += change * self.sign_factor
        


class DefenseStatus(Status):
    """
    This status blocks incoming damage.
    """
    def __init__(self, status_id, description):
        """
        Initialize a new DefenseStatus.
        """
        super().__init__(status_id, description, applies_immediately=False)

    def calculate_net_damage(
            self, subject, level, incoming_damage, status_registry
            ) -> int:
        """
        Return damage after blocking and handle defense reduction from taking
        damage.
        """
        net_damage = self.modify_value(incoming_damage, level, True, 0)
        defense_to_remove = net_damage - incoming_damage
        subject.status_manager.change_status(
            self.status_id, defense_to_remove, subject, status_registry
            )
        return net_damage


class PoisonStatus(Status):
    """
    This status deals Poison Damage at the start of each turn.
    """
    def __init__(self, status_id, description):
        """
        Initialize a new PoisonStatus.
        """
        super().__init__(status_id, description, applies_immediately=False)

    def trigger_on_turn(self, subject, level, status_registry):
        """
        Activate the status effect when requested by caller.
        """
        damage_type = c.DamageTypes.POISON.name
        subject.take_damage(None, level, damage_type, status_registry)


class RegenerationStatus(Status):
    """
    This status restores health at the start of each turn.
    """
    def __init__(self, status_id, description):
        """
        Initialize a new RegenerationStatus.
        """
        super().__init__(status_id, description, applies_immediately=False)

    def trigger_on_turn(self, subject, level, status_registry):
        subject.change_resource(c.Resources.HEALTH.name, level)


class EvasionStatus(Status):
    """
    This status randomly prevents all or zero incoming damage.
    """
    def __init__(self, status_id, description):
        """
        Initialize a new EvasionStatus.
        """
        super().__init__(status_id, description, applies_immediately=False)

    def calculate_evasion_damage(self, level, incoming_damage) -> int:
        """
        Return the damage to be taken after winning or losing the dice roll.
        """
        base_probability = c.BASE_EVASION_PROBABILITY
        success_probability = min(base_probability * level, 1.0)
        roll = random.random()
        return 0 if roll >= success_probability else incoming_damage


class CriticalHitStatus(Status):
    """
    This status randomly causes the subject to deal double damage.
    """
    def __init__(self, status_id, description):
        """
        Initialize a new CriticalHitStatus.
        """
        super().__init__(status_id, description, applies_immediately=False)

    def calculate_damage_multiplier(self, level) -> int:
        """
        Randomly calculate the damage multiplier.
        """
        base_probability = c.BASE_CRIT_PROBABILITY
        success_probability = min(base_probability * level, 1.0)
        roll = random.random()
        return c.CRIT_MULTIPLIER if roll >= success_probability else 1


class RestrictCardTypeStatus(Status):
    """
    This status prevents the subject from playing certain tyoes of cards.
    """
    def __init__(self, status_id, description, restricted_types):
        """
        Initialize a new RestrictCardStatus.
        """
        super().__init__(status_id, description, applies_immediately=True)
        self.restricted_types = restricted_types

    def is_card_playable(self, card_type) -> bool:
        """
        Check if the given card type is allowed to be played.
        """
        return card_type not in self.restricted_types


class FilterEffectStatus(Status):
    """
    This status allows only certain effects to resolve.
    """
    def __init__(self, status_id, description, allowed_effect, blocked_effect):
        """
        Initialize a new FilterEffectStatus.
        """
        super().__init__(status_id, description, applies_immediately=False)
        self.allowed_effect = allowed_effect
        self.blocked_effect = blocked_effect

    def effect_can_resolve(self, effect_id) -> bool:
        """
        Check if the given effect is allowed to resolve.
        """
        if self.blocked_effect and effect_id == self.blocked_effect:
            return False
        if self.allowed_effect and effect_id != self.allowed_effect:
            return False
        return True


class LimitCardPlayStatus(Status):
    """
    This status prevents a combatant from playing more than a certain number of
    cards per turn.
    """
    def __init__(self, status_id, description, max_cards_per_turn):
        """
        Initialize a new LimitCardPlayStatus.
        """
        super().__init__(status_id, description, applies_immediately=False)
        self.card_limit = max_cards_per_turn


class BlockMagicStatus(Status):
    """
    This type of status blocks incoming non-physical damage and redirects it.
    """
    def __init__(self, status_id, description):
        """
        Initialize a new BlockMagicStatus.
        """
        super().__init__(status_id, description, applies_immediately=False)

    def calculate_block(self, damage_amount, damage_type, status_level):
        """
        Get the net damage and blocked damage amounts.
        """
        assert c.DamageTypes[damage_type]
        if damage_type != c.DamageTypes.PHYSICAL.name:
            new_amount = max(damage_amount - status_level, 0)
            blocked_damage = damage_amount - new_amount
            return new_amount, blocked_damage
        return damage_amount, 0


class AverageCostStatus(Status):
    """
    This status averages the costs of cards in hand.
    """
    def __init__(self, status_id, description):
        """
        Initialize a new AverageCostStatus.
        """
        super().__init__(status_id, description, applies_immediately=True)

    def trigger_on_change(self, subject, level):
        """
        Perform the cost averaging.
        """
        if level <= 0 or not subject.card_manager.hand:
            return
        sum_cost = 0
        for card in subject.card_manager.hand:
            sum_cost += card.get_cost(False)
        average_cost = round(sum_cost / len(subject.card_manager.hand))
        for card in subject.card_manager.hand:
            card.override_cost = average_cost

    def expire(self, subject, logger):
        """
        Reset costs.
        """
        super().expire(subject, logger)
        for card in subject.card_manager.hand:
            card.reset_override_cost()


class FlagStatus(Status):
    """
    This type of status does something just by being present and has no other
    behavior.
    """
    def __init__(self, status_id, description):
        """
        Initialize a new FlagStatus.
        """
        super().__init__(status_id, description, applies_immediately=False)


class MulliganStatus(Status):
    """
    This status allows the player to discard and redraw at the start of their
    turn.
    """
    def __init__(self, status_id, description):
        """
        Initialize a new MulliganStatus.
        """
        super().__init__(status_id, description, applies_immediately=False)

    def do_redraw(self, subject, level, text_interface, registries):
        """
        Prompt the user to discard cards, then draw that many cards.
        """
        if subject.is_enemy:
            return

        discard_selection = text_interface.discard_prompt(
            subject, level, True, registries.effects
            )
        if not discard_selection:
            return
        discard_selection.sort(reverse=True)
        cards_discarded = 0
        for card_index in discard_selection:
            card = subject.card_manager.hand[card_index]
            subject.card_manager.discard(card, subject, registries.statuses)
            cards_discarded += 1
        subject.card_manager.draw(
            subject, registries.statuses, cards_discarded
            )


class ReturnFromDiscardStatus(Status):
    """
    This status allows the subject to draw from their discard pile.
    """
    def __init__(self, status_id, description):
        """
        Initialize a new ReturnFromDiscardStatus.
        """
        super().__init__(status_id, description, applies_immediately=False)

    def draw_from_discard(
            self, subject, level, text_interface, status_registry
            ) -> int:
        """
        Move player selected cards from discard to hand and return the number
        of cards moved.
        """
        count = 0
        selection = text_interface.return_from_discard_prompt(
            subject.card_manager.discard_pile, level
            )
        if not selection:
            return 0
        selection.sort(reverse=True)
        for card_index in selection:
            subject.card_manager.undiscard(
                card_index, subject, status_registry
                )
            count += 1
        return count


class StatusRegistry:
    """
    Holds Status objects in a dictionary to be looked up when needed.
    """
    def __init__(self, statuses_path, event_manager):
        """
        Initialize a new StatusRegistry.
        """
        self.statuses = self._initialize_statuses(statuses_path)
        self.event_manager = event_manager

    def _initialize_statuses(self, filepath) -> dict:
        """
        Create Status objects and file them in a dict.
        """
        status_data = load_json(filepath)
        status_classes = {
            "Status": Status,
            "ModifyEffectStatus": ModifyEffectStatus,
            "ModifyCostStatus": ModifyCostStatus,
            "ModifyMaxResourceStatus": ModifyMaxResourceStatus,
            "ModifyDrawStatus": ModifyDrawStatus,
            "ModifyDamageStatus": ModifyDamageStatus,
            "ModifyAttributeStatus": ModifyAttributeStatus,
            "DefenseStatus": DefenseStatus,
            "PoisonStatus": PoisonStatus,
            "RegenerationStatus": RegenerationStatus,
            "EvasionStatus": EvasionStatus,
            "CriticalHitStatus": CriticalHitStatus,
            "RestrictCardTypeStatus": RestrictCardTypeStatus,
            "FilterEffectStatus": FilterEffectStatus,
            "LimitCardPlayStatus": LimitCardPlayStatus,
            "BlockMagicStatus": BlockMagicStatus,
            "AverageCostStatus": AverageCostStatus,
            "FlagStatus": FlagStatus,
            "MulliganStatus": MulliganStatus,
            "ReturnFromDiscardStatus": ReturnFromDiscardStatus
            }

        statuses = {}

        for status_id, data in status_data.items():
            class_name = data.pop("class") # Extract the class name
            if class_name not in status_classes:
                raise ValueError(f"Unknown status class: {class_name}")

            # Instantiate the status dynamically
            status_class = status_classes[class_name]
            data["status_id"] = status_id
            statuses[status_id] = status_class(**data)

        return statuses

    def get_status(self, status_id) -> Status:
        """
        Get Status object by status id.
        """
        if status_id not in self.statuses:
            raise KeyError(f"Status ID '{status_id}' not found.")
        return self.statuses[status_id]

    def list_statuses(self) -> list:
        """
        Return a list of status ids.
        """
        return list(self.statuses.keys())
