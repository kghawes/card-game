from copy import copy
from utils.prototype import Prototype
from utils.data_loader import load_json
from combatants import Combatant

class Enemy(Combatant):
    def __init__(self, loot):
        self.loot = loot

class EnemyPrototype(Enemy, Prototype):
    def clone(self):
        return copy(self)

class EnemyCache:
    def __init__(self, filename):
        self.enemy_prototypes = self._load_enemy_prototypes(filename)

    def _load_enemy_prototypes(self, filename: str) -> dict:
        enemy_data = load_json(filename)
        prototypes = {}
        for enemy_id, data in enemy_data.items():
            if not all(key in data for key in ["name", "health", "stamina", "loot"]):
                raise ValueError(f"Enemy '{enemy_id}' is missing required fields.")
            prototypes[enemy_id] = EnemyPrototype(
                name=data["name"],
                health=data["damage"],
                stamina=data["stamina"],
                loot=data["loot"]
            )
        return prototypes

    def create_enemy(self, enemy_id: str) -> Enemy:
        if enemy_id not in self.enemy_prototypes:
            raise KeyError(f"Enemy ID '{enemy_id}' not found.")
        return self.enemy_prototypes[enemy_id].clone()

    def list_enemy_prototypes(self) -> list:
        return list(self.enemy_prototypes.keys())
