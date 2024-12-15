from abc import ABC, abstractmethod
from utils.utils import load_json

class Modifier(ABC):
    def __init__(self, name, costliness, effectiveness, rarity):
        self.name = name
        self.costliness = costliness
        self.effectiveness = effectiveness
        self.rarity = rarity
    
    @abstractmethod
    def format_new_name(self, previous_name) -> str:
        pass

class WeaponStyleModifier(Modifier):
    def __init__(self, name, costliness, effectiveness, rarity, enchanted_name):
        super().__init__(name, costliness, effectiveness, rarity)
        self.enchanted_name = enchanted_name
        
    def format_new_name(self, previous_name) -> str:
        return (previous_name + " " + self.name).strip()

class MaterialModifier(Modifier):
    def format_new_name(self, previous_name) -> str:
        return (self.name + " " + previous_name).strip()

class ModifierCache:
    def __init__(self, modifiers_path):
        modifier_data = load_json()