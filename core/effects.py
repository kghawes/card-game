"""
This module defines the Effect class, its child classes, and the
EffectRegistry.
"""
import utils.constants as c

class Effect:
    """Base class representing a card's immediate effect when played."""
    def __init__(self, effect_id, name, target_type_enum=None):
        """Initialize a new Effect."""
        self.effect_id = effect_id
        self.name = name
        self.target_type_enum = target_type_enum

    def resolve(self, source, opponent, level=1, status_registry=None):
        """Base method for polymorphism. Do the thing the effect does."""
        return

    def get_target_combatant(self, source, opponent):
        """Identify the correct Combatant to apply the effect to."""
        if self.target_type_enum == c.TargetTypes.TARGET:
            return opponent
        return source

    def format_id(self, *strings) -> str:
        """Create the effect id by combining its parts."""
        return "_".join([*strings, self.target_type_enum.name])

    def format_name(self, *strings) -> str:
        """Create the effect display name by combining its parts."""
        return " ".join([*strings, self.target_type_enum.value])

    def matches(self, effect_id) -> bool:
        """Check if this effect matches the given type of effect."""
        return effect_id in self.effect_id


class NoEffect(Effect):
    """This effect does nothing. Needed for cards that do nothing."""
    def __init__(self):
        """Initialize a new NoEffect."""
        effect_id = c.EffectNames.NO_EFFECT.name
        effect_name = c.EffectNames.NO_EFFECT.value
        super().__init__(effect_id, effect_name, None)


class ChangeStatusEffect(Effect):
    """This type of effect applies or removes a Status."""
    def __init__(self, effect_name_enum, target_type_enum, status_enum):
        """Initialize a new ChangeStatusEffect."""
        self.target_type_enum = target_type_enum
        self.status_enum = status_enum
        base_id = effect_name_enum.name
        base_name = effect_name_enum.value
        self.effect_id = self.format_id(base_id, status_enum.name)
        self.name = self.format_name(base_name + status_enum.value)
        super().__init__(self.effect_id, self.name, target_type_enum)

    def resolve(self, source, opponent, level, status_registry):
        """Change the status by the amount indicated."""
        subject = self.get_target_combatant(source, opponent)
        status_id = self.status_enum.name

        if self.matches(c.EffectNames.REMOVE.name):
            level *= -1

        subject.status_manager.change_status(
            status_id, level, subject, status_registry
            )


class DamageEffect(Effect):
    """This type of effect deals damage."""
    def __init__(self, target_type_enum, damage_type_enum):
        """Initialize a new DamageEffect."""
        self.target_type_enum = target_type_enum
        self.damage_type_enum = damage_type_enum
        base_id = damage_type_enum.name
        base_name = damage_type_enum.value
        effect_id = self.format_id(base_id, c.EffectNames.DAMAGE.name)
        name = self.format_name(base_name, c.EffectNames.DAMAGE.value)
        super().__init__(effect_id, name, target_type_enum)

    def resolve(self, source, opponent, level, status_registry):
        """The target of the effect takes damage."""
        subject = self.get_target_combatant(source, opponent)
        subject.take_damage(level, self.damage_type_enum, status_registry)


class ChangeResourceEffect(Effect):
    """This type of effect changes the current value of a Resource."""
    def __init__(self, effect_name_enum, target_type_enum, resource_enum):
        """Initialize a new ChangeResourceEffect."""
        self.resource_enum = resource_enum
        self.target_type_enum = target_type_enum
        effect_id = self.format_id(effect_name_enum.name, resource_enum.name)
        name = self.format_name(effect_name_enum.value, resource_enum.value)
        super().__init__(effect_id, name, target_type_enum)

    def resolve(self, source, opponent, level, status_registry):
        """Change the resource's current value by the amount indicated."""
        if self.matches(c.EffectNames.DRAIN.name):
            level *= -1
        subject = self.get_target_combatant(source, opponent)
        subject.change_resource(self.resource_enum.name, level)


class PickpocketEffect(Effect):
    """This effect lets you look at the top cards of your opponent's
    deck and play one of them."""
    def __init__(self):
        """Initialize a new PickpocketEffect."""
        effect_id = c.EffectNames.PICKPOCKET.name
        effect_name = c.EffectNames.PICKPOCKET.value
        super().__init__(effect_id, effect_name)

    def resolve(self, source, opponent, level, status_registry):
        """Show opponent cards and play one."""
        # target.card_manager.show_top_cards_in_deck(level)
        # ....
        pass


class HandEffect(Effect):
    """This type of effect draws or discards cards."""
    def __init__(self, effect_name_enum, target_type_enum, is_draw_effect):
        """Initialize a new HandEffect."""
        effect_id = effect_name_enum.name
        name = effect_name_enum.value
        super().__init__(effect_id, name, target_type_enum)
        self.is_draw_effect = is_draw_effect

    def resolve(self, source, opponent, level, status_registry):
        """Draw or discard card(s)."""
        subject = self.get_target_combatant(source, opponent)
        if level == 0:
            return
        if self.is_draw_effect:
            subject.card_manager.draw(level)
        else:
            pass


class EffectRegistry:
    """This class holds effect data and provides access to the effects."""
    def __init__(self, status_registry):
        """Initialize a new EffectRegistry."""
        self.effects = self._register_effects(status_registry)

    def _register_effects(self, status_registry) -> dict:
        """Create the Effect objects and file them in the dict."""
        effects = {}

        effects[c.EffectNames.NO_EFFECT.name] = NoEffect()
        effects[c.EffectNames.PICKPOCKET.name] = PickpocketEffect()

        for target_type in c.TargetTypes:
            for status_id in status_registry.list_statuses():
                apply_status_effect = ChangeStatusEffect(
                    c.EffectNames.APPLY, target_type, c.StatusNames[status_id]
                    )
                remove_status_effect = ChangeStatusEffect(
                    c.EffectNames.REMOVE, target_type, c.StatusNames[status_id]
                    )
                effects[apply_status_effect.effect_id] = apply_status_effect
                effects[remove_status_effect.effect_id] = remove_status_effect

            for damage_type in c.DamageTypes:
                damage_effect = DamageEffect(target_type, damage_type)
                effects[damage_effect.effect_id] = damage_effect

            for resource in c.Resources:
                if resource == c.Resources.HEALTH:
                    restore_health_effect = ChangeResourceEffect(
                        c.EffectNames.RESTORE, target_type, resource
                        )
                    health_id = restore_health_effect.effect_id
                    effects[health_id] = restore_health_effect
                else:
                    drain_effect = ChangeResourceEffect(
                        c.EffectNames.DRAIN, c.TargetTypes.SELF, resource
                        )
                    restore_effect = ChangeResourceEffect(
                        c.EffectNames.RESTORE, c.TargetTypes.SELF, resource
                        )
                    effects[drain_effect.effect_id] = drain_effect
                    effects[restore_effect.effect_id] = restore_effect

        return effects

    def get_effect(self, effect_id) -> Effect:
        """Get the Effect object with the given id."""
        if effect_id not in self.effects:
            raise KeyError(f"Effect ID '{effect_id}' not found.")
        return self.effects[effect_id]
