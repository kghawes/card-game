import Combatant

class CharacterClass(Enum):
    def x(): return

class Player(Combatant):
    def __init__(self, character_class):
        super().__init__("", 10, 3)