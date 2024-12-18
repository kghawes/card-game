from utils.constants import Resources, DamageTypes, EffectNames, StatusNames, TargetTypes
from utils.utils import load_json

class Effect:
    def __init__(self, effect_id, name, target_type_enum=None):
        self.effect_id = effect_id
        self.name = name
        self.target_type_enum = target_type_enum
    
    def resolve(self, source, opponent, level=1):
        return
    
    def get_target_combatant(self, source, opponent):
        return opponent if self.target_type_enum == TargetTypes.TARGET else source
    
    def format_string(self, separator, *strings) -> str:
        return separator.join(strings)
    
    def format_id(self, *strings) -> str:
        return self.format_string("_", *strings, self.target_type_enum.name)
    
    def format_name(self, *strings) -> str:
        return self.format_string(" ", *strings, self.target_type_enum.value)

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
    
    def resolve(self, source, opponent, level):
        subject = self.get_target_combatant(source, opponent)
        subject.status_manager.change_status(self.status_enum.name, level)

class DamageEffect(Effect):
    def __init__(self, target_type_enum, damage_type_enum):
        self.target_type_enum = target_type_enum
        self.damage_type_enum = damage_type_enum
        effect_id = self.format_id(damage_type_enum.name, EffectNames.DAMAGE.name)
        name = self.format_name(damage_type_enum.value, EffectNames.DAMAGE.value)
        super().__init__(effect_id, name, target_type_enum)
        
    def resolve(self, source, opponent, level):
        subject = self.get_target_combatant(source, opponent)
        subject.take_damage(level, self.damage_type_enum)

class RestoreEffect(Effect):
    def __init__(self, target_type_enum, resource_enum):
        self.resource_enum = resource_enum
        self.target_type_enum = target_type_enum
        effect_id = self.format_id(EffectNames.RESTORE.name, resource_enum.name)
        name = self.format_name(EffectNames.RESTORE.value, resource_enum.value.display) 
        super().__init__(effect_id, name, target_type_enum)
    
    def resolve(self, source, opponent, level):
        subject = self.get_target_combatant(source, opponent)
        subject.gain_resource(self.resource_enum, level)

class PickpocketEffect(Effect):
    def __init__(self):
        super().__init__(EffectNames.PICKPOCKET.name, EffectNames.PICKPOCKET.value)
    
    def resolve(self, source, opponent, level):
        # target.card_manager.show_top_cards_in_deck(level)
        # ....
        pass

class EffectRegistry:
    def __init__(self, effects_path):
        self.effects = self._register_effects(effects_path)

    def _create_effect(self, effect_id, data):
        effect_type = data["TYPE"]
        target_type = TargetTypes[data["TARGET_TYPE"].upper()]
        
        if effect_type == EffectNames.NO_EFFECT.name:
            return NoEffect()
        elif effect_type == EffectNames.APPLY_STATUS.name:
            status_id = StatusNames[data["STATUS"].upper()]
            return ChangeStatusEffect(EffectNames.APPLY_STATUS, target_type, status_id)
        elif effect_type == EffectNames.REMOVE_STATUS.name:
            status_id = StatusNames[data["STATUS"].upper()]
            return ChangeStatusEffect(EffectNames.REMOVE_STATUS, target_type, status_id)
        elif effect_type == EffectNames.DAMAGE.name:
            damage_type = DamageTypes[data["DAMAGE_TYPE"].upper()]
            return DamageEffect(target_type, damage_type)
        elif effect_type == EffectNames.RESTORE.name:
            resource = Resources[data["RESOURCE"].upper()]
            return RestoreEffect(target_type, resource)
        elif effect_type == EffectNames.PICKPOCKET.name:
            return PickpocketEffect()
        else:
            raise ValueError(f"Unknown effect type '{effect_type}'.")

    def _register_effects(self, path):
        effects = {}
        data = load_json(path)

        for effect_id, effect_data in data.items():
            effect = self._create_effect(effect_id, effect_data)
            effects[effect_id] = effect

        return effects

    def get_effect(self, effect_id) -> Effect:
        if effect_id not in self.effects:
            raise KeyError(f"Effect ID '{effect_id}' not found.")
        return self.effects[effect_id]
