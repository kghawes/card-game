from utils.utils import Prototype, load_json
from core.combatants import Combatant
from gameplay.treasure import Treasure

class Enemy(Combatant):
    def __init__(
            self, name, max_health, max_stamina, max_magicka, deck, card_cache, 
            status_registry, loot
            ):
        super().__init__(
            name, max_health, max_stamina, max_magicka, deck, card_cache, 
            status_registry
            )
        self.loot = Treasure(loot)


class EnemyPrototype(Prototype):
    def __init__(self, name, max_health, max_stamina, max_magicka, deck, loot):
        self.name = name
        self.max_health = max_health
        self.max_stamina = max_stamina
        self.max_magicka = max_magicka
        self.deck = deck  # Save raw deck data
        self.loot = loot

    def clone(self, card_cache, status_registry):
        return Enemy(
            name=self.name,
            max_health=self.max_health,
            max_stamina=self.max_stamina,
            max_magicka=self.max_magicka,
            deck=self.deck,  # Pass raw deck to Enemy
            card_cache=card_cache,
            status_registry = status_registry,
            loot=self.loot
        )


class EnemyCache:
    def __init__(self, filename):
        self.enemy_prototypes = self._load_enemy_prototypes(filename)

    def _load_enemy_prototypes(self, filename) -> dict:
        enemy_data = load_json(filename)
        prototypes = {}
        for enemy_id, data in enemy_data.items():
            if not all(key in data for key in [
                    "name",
                    "max_health",
                    "max_stamina",
                    "max_magicka",
                    "deck",
                    "loot"
                    ]):
                raise ValueError(
                    f"Enemy '{enemy_id}' is missing required fields."
                    )
            prototypes[enemy_id] = EnemyPrototype(
                name=data["name"],
                max_health=data["max_health"],
                max_stamina=data["max_stamina"],
                max_magicka=data["max_magicka"],
                deck=data["deck"],  # Pass raw deck
                loot=data["loot"]
            )
        return prototypes

    def create_enemy(self, enemy_id, card_cache, status_registry) -> Enemy:
        if enemy_id not in self.enemy_prototypes:
            raise KeyError(f"Enemy ID '{enemy_id}' not found.")
        prototype = self.enemy_prototypes[enemy_id]
        enemy = prototype.clone(card_cache, status_registry)
        return enemy

    def list_enemy_prototypes(self) -> list:
        return list(self.enemy_prototypes.keys())

