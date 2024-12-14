from copy import copy
from utils.utils import Prototype, load_json
from core.combatants import Combatant
from gameplay.treasure import Treasure

class Enemy(Combatant):
    def __init__(self, name, max_health, max_stamina, deck, card_cache, loot):
        super().__init__(name, max_health, max_stamina, deck, card_cache)
        self.loot = Treasure(loot)

class EnemyPrototype(Enemy, Prototype):
    def clone(self):
        return copy(self)

class EnemyCache:
    def __init__(self, filename, card_cache):
        self.enemy_prototypes = self._load_enemy_prototypes(filename, card_cache)

    def _load_enemy_prototypes(self, filename: str, cards) -> dict:
        enemy_data = load_json(filename)
        prototypes = {}
        for enemy_id, data in enemy_data.items():
            if not all(key in data for key in ["name", "max_health", "max_stamina", "deck", "loot"]):
                raise ValueError(f"Enemy '{enemy_id}' is missing required fields.")
            prototypes[enemy_id] = EnemyPrototype(
                name=data["name"],
                max_health=data["max_health"],
                max_stamina=data["max_stamina"],
                deck=data["deck"],
                card_cache=cards,
                loot=data["loot"]
            )
        return prototypes

    def create_enemy(self, enemy_id: str) -> Enemy:
        if enemy_id not in self.enemy_prototypes:
            raise KeyError(f"Enemy ID '{enemy_id}' not found.")
        return self.enemy_prototypes[enemy_id].clone()

    def list_enemy_prototypes(self) -> list:
        return list(self.enemy_prototypes.keys())
