from abc import ABC, abstractmethod
from constants import CardTypes

class Card(ABC):
    def __init__(self, card_id, name, card_type, effects):
        self.card_id = card_id
        self.name = name
        self.card_type = card_type
        self.effects = effects[:]
    
    @abstractmethod
    def apply_modifier(modifier):
        pass

class WeaponCard(Card):
    def __init__(self, card_id, name, effects):
        super().__init__(card_id, name, CardTypes.WEAPON, effects)
    
    def apply_modifier(modifier):
        
        

class BaseCardTemplates:
    def