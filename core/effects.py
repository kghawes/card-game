from abc import ABC, abstractmethod
from utils.constants import Resources, DamageTypes, EffectNames

class Effect(ABC):
    def __init__(self, effect_id, name):
        self.effect_id = effect_id
        self.name = name
    
    @abstractmethod
    def resolve(self, source, target, *args, **kwargs):
        pass
    
    def format_id(self, first_part, second_part) -> str:
        return first_part + "_" + second_part
    
    def format_name(self, first_part, second_part) -> str:
        return first_part + " " + second_part

class DamageEffect(Effect):
    def __init__(self, damage_type):
        effect_id = self.format_id(damage_type.name, EffectNames.DAMAGE.name)
        name = self.format_name(damage_type.value, EffectNames.DAMAGE.value)
        super().__init__(effect_id, name)
        self.damage_type = damage_type
        
    def resolve(self, source, target, amount = 0):
        target.take_damage(amount, self.damage_type)

class FireDamageEffect(DamageEffect):
    def __init__(self):
        super().__init__(DamageTypes.FIRE)

class RestoreEffect(Effect):
    def __init__(self, resource):
        effect_id = self.format_id(EffectNames.RESTORE.name, resource.name)
        name = self.format_name(EffectNames.RESTORE.value, resource.value) 
        super().__init__(effect_id, name)
    
    def resolve(self, source, target, amount = 0):
        if self.stat == Resources.HEALTH.value:
            source.gain_health(amount)
        elif self.stat == Resources.STAMINA.value:
            source.gain_stamina(amount)
        # elif self.stat == Resources.MAGICKA.value:
        #     source.gain_magicka(amount)

class RestoreHealthEffect(RestoreEffect):
    def __init__(self):
        super().__init__(Resources.HEALTH)