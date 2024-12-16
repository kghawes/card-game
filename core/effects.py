from abc import ABC, abstractmethod
from utils.constants import Resources, DamageTypes, EffectNames, StatusNames

class Effect(ABC):
    def __init__(self, effect_id, name):
        self.effect_id = effect_id
        self.name = name
    
    @abstractmethod
    def resolve(self, source, target, *args, **kwargs) -> bool: # return whether the effect ended combat
        pass
    
    def format_id(self, first_part, second_part) -> str:
        return first_part + "_" + second_part
    
    def format_name(self, first_part, second_part) -> str:
        return first_part + " " + second_part

class NoEffect(Effect):
    def __init__(self):
        super().__init__(EffectNames.NO_EFFECT.name, EffectNames.NO_EFFECT.value)
    
    def resolve(self, source, target) -> bool:
        return False

class DamageEffect(Effect):
    def __init__(self, damage_type):
        effect_id = self.format_id(damage_type.name, EffectNames.DAMAGE.name)
        name = self.format_name(damage_type.value, EffectNames.DAMAGE.value)
        super().__init__(effect_id, name)
        self.damage_type = damage_type
        
    def resolve(self, source, target, amount = 0) -> bool:
        return target.take_damage(amount, self.damage_type)

class RestoreEffect(Effect):
    def __init__(self, resource):
        effect_id = self.format_id(EffectNames.RESTORE.name, resource.name)
        name = self.format_name(EffectNames.RESTORE.value, resource.value) 
        super().__init__(effect_id, name)
    
    def resolve(self, source, target, amount = 0) -> bool:
        if self.stat == Resources.HEALTH.value:
            source.gain_health(amount)
        elif self.stat == Resources.STAMINA.value:
            source.gain_stamina(amount)
        elif self.stat == Resources.MAGICKA.value:
            source.gain_magicka(amount)
        return False

class PickpocketEffect(Effect):
    def __init__(self):
        super().__init__(EffectNames.PICKPOCKET.name, EffectNames.PICKPOCKET.value)
    
    def resolve(self, source, target, level = 1) -> bool:
        # target.card_manager.show_top_cards_in_deck(level)
        # ....
        return False

class GainDefenseEffect(Effect):
    def __init__(self):
        super().__init__(EffectNames.GAIN_DEFENSE.name, EffectNames.GAIN_DEFENSE.value)
    
    def resolve(self, source, target, amount = 0) -> bool:
        target.status_manager.apply(StatusNames.DEFENSE.name)
        return False

class EffectRegistry:
    def __init__(self):
        self.effects = self._initialize_effects()
    
    def _initialize_effects(self) -> dict:
        physical_damage_effect = DamageEffect(DamageTypes.PHYSICAL)
        fire_damage_effect = DamageEffect(DamageTypes.FIRE)
        frost_damage_effect = DamageEffect(DamageTypes.FROST)
        shock_damage_effect = DamageEffect(DamageTypes.SHOCK)
        poison_damage_effect = DamageEffect(DamageTypes.POISON)
        
        restore_health_effect = RestoreEffect(Resources.HEALTH)
        restore_stamina_effect = RestoreEffect(Resources.STAMINA)
        
        effects = {
            physical_damage_effect.effect_id: physical_damage_effect,
            fire_damage_effect.effect_id: fire_damage_effect,
            frost_damage_effect.effect_id: frost_damage_effect,
            shock_damage_effect.effect_id: shock_damage_effect,
            poison_damage_effect.effect_id: poison_damage_effect,
            restore_health_effect.effect_id: restore_health_effect,
            restore_stamina_effect.effect_id: restore_stamina_effect
            }
        
        return effects
    
    def get_effect(self, effect_id) -> Effect:
        if effect_id not in self.effects:
            raise KeyError(f"Effect ID '{effect_id}' not found.")
        return self.effects[effect_id]