# Treasure Class
class Treasure:
    def __init__(self, gold):
        self.gold = gold

# Quest and Encounter Classes
class Encounter:
    def __init__(self, enemy):
        self.enemy = enemy

class Quest:
    def __init__(self, description, encounter):
        self.description = description
        self.encounter = encounter

game_loop()