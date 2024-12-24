from utils.constants import Resources, DamageTypes, EffectNames, StatusNames, TargetTypes

class Effect:
    def __init__(self, effect_id, name, target_type_enum=None):
        self.effect_id = effect_id
        self.name = name
        self.target_type_enum = target_type_enum
    
    def resolve(self, source, opponent, level=1, status_registry=None):
        return
    
    def get_target_combatant(self, source, opponent):
        return opponent if self.target_type_enum == TargetTypes.TARGET else source
    
    def format_string(self, separator, *strings) -> str:
        return separator.join(strings)
    
    def format_id(self, *strings) -> str:
        return self.format_string("_", *strings, self.target_type_enum.name)
    
    def format_name(self, *strings) -> str:
        return self.format_string(" ", *strings, self.target_type_enum.value)
    
    def matches(self, effect_id) -> bool:
        return effect_id in self.effect_id

class NoEffect(Effect):
    def __init__(self):
        super().__init__(EffectNames.NO_EFFECT.name, EffectNames.NO_EFFECT.value, None)

class ChangeStatusEffect(Effect):
    def __init__(self, effect_name_enum, target_type_enum, status_enum):
        self.target_type_enum = target_type_enum
        self.status_enum = status_enum
        self.effect_id = self.format_id(effect_name_enum.name, status_enum.name)
        self.name = self.format_name(effect_name_enum.value + status_enum.value)
        super().__init__(self.effect_id, self.name, target_type_enum)
    
    def resolve(self, source, opponent, level, status_registry):
        subject = self.get_target_combatant(source, opponent)
        status_id = self.status_enum.name
        if EffectNames.REMOVE.name in self.effect_id:
            level *= -1
        subject.status_manager.change_status(status_id, level)
        
        if subject.status_manager.has_status(status_id):
            status = status_registry.get_status(status_id)
            if status.applies_immediately:
                status.trigger_on_apply(subject, subject.status_manager.get_status_level(status_id))            

class DamageEffect(Effect):
    def __init__(self, target_type_enum, damage_type_enum):
        self.target_type_enum = target_type_enum
        self.damage_type_enum = damage_type_enum
        effect_id = self.format_id(damage_type_enum.name, EffectNames.DAMAGE.name)
        name = self.format_name(damage_type_enum.value, EffectNames.DAMAGE.value)
        super().__init__(effect_id, name, target_type_enum)
        
    def resolve(self, source, opponent, level, status_registry):
        subject = self.get_target_combatant(source, opponent)
        subject.take_damage(level, self.damage_type_enum, status_registry)

class ChangeResourceEffect(Effect):
    def __init__(self, effect_name_enum, target_type_enum, resource_enum):
        self.resource_enum = resource_enum
        self.target_type_enum = target_type_enum
        effect_id = self.format_id(effect_name_enum.name, resource_enum.name)
        name = self.format_name(effect_name_enum.value, resource_enum.value) 
        super().__init__(effect_id, name, target_type_enum)
    
    def resolve(self, source, opponent, level, status_registry):
        if EffectNames.DRAIN in self.effect_id:
            level *= -1
        subject = self.get_target_combatant(source, opponent)
        subject.change_resource(self.resource_enum, level)

class PickpocketEffect(Effect):
    def __init__(self):
        super().__init__(EffectNames.PICKPOCKET.name, EffectNames.PICKPOCKET.value)
    
    def resolve(self, source, opponent, level, status_registry):
        # target.card_manager.show_top_cards_in_deck(level)
        # ....
        pass
    
class HandEffect(Effect):
    def __init__(self, effect_name_enum, target_type_enum, is_draw_effect):
        effect_id = effect_name_enum.name
        name = effect_name_enum.value
        super().__init__(effect_id, name, target_type_enum)
        self.is_draw_effect = is_draw_effect
    
    def resolve(self, source, opponent, level, status_registry):
        subject = self.get_target_combatant(source, opponent)
        if level == 0: 
            return
        if self.is_draw_effect:
            subject.card_manager.draw(level)
        else:
            pass

class EffectRegistry:
    def __init__(self, effects_path, status_registry):
        self.effects = self._register_effects(effects_path, status_registry)

    def _register_effects(self, path, status_registry):
        effects = {}
        
        effects[EffectNames.NO_EFFECT.name] = NoEffect()
        effects[EffectNames.PICKPOCKET.name] = PickpocketEffect()
        
        for target_type in TargetTypes:
            for status_id in status_registry.list_statuses():
                apply_status_effect = ChangeStatusEffect(EffectNames.APPLY, target_type, StatusNames[status_id])
                remove_status_effect = ChangeStatusEffect(EffectNames.REMOVE, target_type, StatusNames[status_id])
                effects[apply_status_effect.effect_id] = apply_status_effect
                effects[remove_status_effect.effect_id] = remove_status_effect
            
            for damage_type in DamageTypes:
                damage_effect = DamageEffect(target_type, damage_type)
                effects[damage_effect.effect_id] = damage_effect
            
            for resource in Resources:
                if resource == Resources.GOLD:
                    continue
                restore_effect = ChangeResourceEffect(EffectNames.RESTORE, target_type, resource)
                if resource != Resources.HEALTH:
                    drain_effect = ChangeResourceEffect(EffectNames.DRAIN, target_type, resource)
                    effects[drain_effect.effect_id] = drain_effect
                effects[restore_effect.effect_id] = restore_effect

        return effects

    def get_effect(self, effect_id) -> Effect:
        if effect_id not in self.effects:
            raise KeyError(f"Effect ID '{effect_id}' not found.")
        return self.effects[effect_id]
