"""
This module defines the Effect class, its child classes, and the
EffectRegistry.
"""
import utils.constants as c

class Effect:
    """
    Base class representing a card's immediate effect when played.
    """
    def __init__(self, effect_id, name, description, target_type_enum=None):
        """
        Initialize a new Effect.
        """
        self.effect_id = effect_id
        self.name = name
        self.description = description
        self.target_type_enum = target_type_enum

    def resolve(self, source, opponent, level=1, status_registry=None):
        """
        Base method for polymorphism. Do the thing the effect does.
        """
        return

    def get_target_combatant(self, source, opponent):
        """
        Identify the correct Combatant to apply the effect to.
        """
        if self.target_type_enum == c.TargetTypes.TARGET:
            return opponent
        return source

    def format_id(self, *strings) -> str:
        """
        Create the effect id by combining its parts.
        """
        return "_".join([*strings, self.target_type_enum.name])

    def format_name(self, *strings) -> str:
        """
        Create the effect display name by combining its parts.
        """
        return " ".join([*strings, self.target_type_enum.value])

    def matches(self, effect_id) -> bool:
        """
        Check if this effect matches the given type of effect.
        """
        return effect_id in self.effect_id


class NoEffect(Effect):
    """
    This effect does nothing. Needed for cards that do nothing.
    """
    def __init__(self):
        """
        Initialize a new NoEffect.
        """
        effect_id = c.EffectNames.NO_EFFECT.name
        effect_name = c.EffectNames.NO_EFFECT.value
        super().__init__(effect_id, effect_name, "", None)
    
    def resolve(self, source, opponent, level=1, status_registry=None):
        """
        This effect does nothing.
        """
        status_registry.event_manager.logger.log(
            f"Nothing happened!"
            )


class ChangeStatusEffect(Effect):
    """
    This type of effect applies or removes a Status.
    """
    def __init__(self, effect_name_enum, description, target_type_enum, status_enum):
        """
        Initialize a new ChangeStatusEffect.
        """
        self.target_type_enum = target_type_enum
        self.status_enum = status_enum
        base_id = effect_name_enum.name
        base_name = effect_name_enum.value
        self.effect_id = self.format_id(base_id, status_enum.name)
        self.name = self.format_name(base_name, status_enum.value)
        super().__init__(self.effect_id, self.name, description, target_type_enum)

    def resolve(self, source, opponent, level, status_registry):
        """
        Change the status by the amount indicated.
        """
        subject = self.get_target_combatant(source, opponent)
        status_id = self.status_enum.name

        if self.matches(c.EffectNames.REMOVE.name):
            level *= -1
            sign_str = "-"
        else:
            sign_str = "+"

        subject.status_manager.change_status(
            status_id, level, subject, status_registry
            )
        
        status_name = status_registry.get_status(status_id).name
        status_registry.event_manager.logger.log(
            f"{sign_str}{level} {status_name} applied to {subject.name}."
        )


class DispelEffect(Effect):
    """
    This type of effect decreases levels from all active statuses.
    """
    def __init__(self, effect_name_enum, description, target_type_enum):
        """
        Initialize a new DispelEffect.
        """
        self.effect_id = self.format_id(effect_name_enum.name)
        self.name = self.format_name(effect_name_enum.value)
        self.target_type_enum = target_type_enum
        super().__init__(self.effect_id, self.name, description, target_type_enum)

    def resolve(self, source, opponent, level, status_registry):
        """
        Reduce active statuses on the subject.
        """
        subject = self.get_target_combatant(source, opponent)
        subject.status_manager.change_all_statuses(
            -level, subject, status_registry # should exclude defense
            )


class DamageEffect(Effect):
    """
    This type of effect deals damage.
    """
    def __init__(self, description, target_type_enum, damage_type_enum):
        """
        Initialize a new DamageEffect.
        """
        self.target_type_enum = target_type_enum
        self.damage_type_enum = damage_type_enum
        base_id = damage_type_enum.name
        base_name = damage_type_enum.value
        effect_id = self.format_id(base_id, c.EffectNames.DAMAGE.name)
        name = self.format_name(base_name, c.EffectNames.DAMAGE.value)
        super().__init__(effect_id, name, description, target_type_enum)

    def resolve(self, source, opponent, level, status_registry):
        """
        The target of the effect takes damage.
        """
        subject = self.get_target_combatant(source, opponent)
        subject.take_damage(
            source, level, self.damage_type_enum.name, status_registry
            )


class ChangeResourceEffect(Effect):
    """
    This type of effect changes the current value of a Resource.
    """
    def __init__(self, effect_name_enum, description, target_type_enum, resource_enum):
        """
        Initialize a new ChangeResourceEffect.
        """
        self.resource_enum = resource_enum
        self.target_type_enum = target_type_enum
        effect_id = self.format_id(effect_name_enum.name, resource_enum.name)
        name = self.format_name(effect_name_enum.value, resource_enum.value)
        super().__init__(effect_id, name, description, target_type_enum)

    def resolve(self, source, opponent, level, status_registry):
        """
        Change the resource's current value by the amount indicated.
        """
        subject = self.get_target_combatant(source, opponent)
        subject.change_resource(self.resource_enum.name, level)
        action_string = "restored" if level > 0 else "drained"
        status_registry.event_manager.logger.log(
            f"{abs(level)} {self.resource_enum.value} {action_string}!"
        )


class HandEffect(Effect):
    """
    This type of effect draws or discards cards.
    """
    def __init__(self, effect_name_enum, description, is_draw_effect):
        """
        Initialize a new HandEffect.
        """
        effect_id = effect_name_enum.name
        name = effect_name_enum.value
        super().__init__(effect_id, name, description, c.TargetTypes.SELF)
        self.is_draw_effect = is_draw_effect

    def resolve(self, source, opponent, level, status_registry):
        """
        Draw or discard card(s).
        """
        subject = source
        if level == 0:
            return
        if self.is_draw_effect:
            subject.card_manager.draw(subject, status_registry, level)
            status_registry.event_manager.logger.log(
                f"{level} cards drawn!"
                )
        else:
            subject.card_manager.discard_random(
                level, subject, status_registry
                )
            status_registry.event_manager.logger.log(
                f"{level} cards discarded!"
                )


class JumpEffect(Effect):
    """
    This effect reduces the cost of the most costly card in hand.
    """
    def __init__(self, description):
        """
        Initialize a new JumpEffect.
        """
        effect_id = c.EffectNames.JUMP.name
        name = c.EffectNames.JUMP.value
        super().__init__(effect_id, name, description, c.TargetTypes.SELF)

    def resolve(self, source, opponent, level, status_registry):
        """
        Reduce the cost of the most costly card in hand.
        """
        subject = source
        hand = subject.card_manager.hand
        highest_cost_card = None

        for card in hand:
            if not highest_cost_card or \
            card.get_cost(False) > highest_cost_card.get_cost(False):
                highest_cost_card = card

        highest_cost_card.change_temp_cost_modifier(-level)

        status_manager = subject.status_manager
        levitate = c.StatusNames.LEVITATE.name
        if status_manager.has_status(levitate, subject, status_registry):
            status_registry.get_status(levitate).trigger_on_change(
                subject, status_manager.get_status_level(levitate)
                )
        
        status_registry.event_manager.logger.log(
            f"{highest_cost_card.name} cost reduced by {level}!"
            )

class EffectRegistry:
    """
    This class holds effect data and provides access to the effects.
    """
    def __init__(self, effects_path, status_registry):
        """
        Initialize a new EffectRegistry.
        """
        self.effects = self._register_effects(effects_path, status_registry)

    def _register_effects(self, effects_path, status_registry) -> dict:
        """
        Create the Effect objects and file them in the dict.
        """
        effects = {}

        descriptions = c.load_json(effects_path)

        # Single-target effects:
        effects[c.EffectNames.NO_EFFECT.name] = NoEffect()

        draw = c.EffectNames.DRAW
        effects[draw.name] = HandEffect(draw, descriptions[draw.name], True)

        discard = c.EffectNames.DISCARD
        effects[discard.name] = HandEffect(discard, descriptions[discard.name], False)

        jump = c.EffectNames.JUMP
        effects[jump.name] = JumpEffect(descriptions[jump.name])

        restore = c.EffectNames.RESTORE
        for resource in c.Resources:
            restore_effect = ChangeResourceEffect(
                restore, descriptions[restore.name], c.TargetTypes.SELF, resource
                )
            effects[restore_effect.effect_id] = restore_effect

        # Multi-target effects:
        for target_type in c.TargetTypes:
            apply = c.EffectNames.APPLY
            remove = c.EffectNames.REMOVE
            apply_description = descriptions[apply.name]
            remove_description = descriptions[remove.name]
            for status_id in status_registry.list_statuses():
                status = status_registry.get_status(status_id)
                description = apply_description.format(
                    status_name=status.name,
                    target=target_type.value,
                    status_description=status.description
                    )
                apply_status_effect = ChangeStatusEffect(
                    c.EffectNames.APPLY, description, target_type, c.StatusNames[status_id]
                    )
                description = remove_description.format(
                    status_name=status.name,
                    target=target_type.value,
                    status_description=status.description
                    )
                remove_status_effect = ChangeStatusEffect(
                    c.EffectNames.REMOVE, description, target_type, c.StatusNames[status_id]
                    )
                effects[apply_status_effect.effect_id] = apply_status_effect
                effects[remove_status_effect.effect_id] = remove_status_effect

            for damage_type in c.DamageTypes:
                description = descriptions[c.EffectNames.DAMAGE.name]
                damage_effect = DamageEffect(description, target_type, damage_type)
                effects[damage_effect.effect_id] = damage_effect

            description = descriptions[c.EffectNames.DISPEL.name]
            dispel_effect = DispelEffect(c.EffectNames.DISPEL, description, target_type)
            effects[dispel_effect.effect_id] = dispel_effect

        return effects

    def get_effect(self, effect_id) -> Effect:
        """
        Get the Effect object with the given id.
        """
        if effect_id not in self.effects:
            raise KeyError(f"Effect ID '{effect_id}' not found.")
        return self.effects[effect_id]
