"""
This module defines the Enemy, EnemyPrototype, and EnemyCache classes. It is
responsible for building a cache of enemy prototypes and generating new enemies
when requested.
"""
from utils.utils import Prototype, load_json
from core.combatants import Combatant
from gameplay.treasure import Treasure

class Enemy(Combatant):
    """
    Represents an enemy combatant.
    """
    def __init__(
            self, name, max_health, max_stamina, max_magicka, deck, card_cache,
            status_registry, loot, card_rewards, event_manager
            ):
        super().__init__(
            name, max_health, max_stamina, max_magicka, deck, card_cache,
            status_registry, True, event_manager
            )
        self.loot = Treasure(loot, card_rewards)
    
    def get_rewards(self, player_class, card_cache) -> dict:
        """
        Get the loot rewards for defeating this enemy.
        """
        return {
            'gold': self.loot.gold,
            'exp': self.loot.exp,
            'cards': self.loot.select_cards(
                1, player_class, card_cache
                )
        }


class EnemyPrototype(Prototype):
    """
    Represents instructions to produce a new Enemy.
    """
    def __init__(self, name, max_health, max_stamina, max_magicka, deck, loot, event_manager):
        """
        Initialize a new EnemyPrototype.
        """
        self.name = name
        self.max_health = max_health
        self.max_stamina = max_stamina
        self.max_magicka = max_magicka
        self.deck = deck
        self.loot = loot
        self.event_manager = event_manager

    def clone(self, card_cache, status_registry, card_rewards) -> Enemy:
        """
        Create an Enemy based on the prototype.
        """
        return Enemy(
            name=self.name,
            max_health=self.max_health,
            max_stamina=self.max_stamina,
            max_magicka=self.max_magicka,
            deck=self.deck,  # Pass raw deck to Enemy
            card_cache=card_cache,
            status_registry = status_registry,
            loot=self.loot,
            card_rewards=card_rewards,
            event_manager=self.event_manager
        )


class EnemyCache:
    """
    Holds all the enemy prototype data.
    """
    def __init__(self, filenames, event_manager):
        """
        Initialize a new EnemyCache.
        """
        self.enemy_prototypes = self._load_enemy_prototypes(filenames, event_manager)

    def _load_enemy_prototypes(self, filenames, event_manager) -> dict:
        """
        Load enemy data from JSON and create the dictionary.
        """
        prototypes = {}
        for path in filenames:
            enemy_data = load_json(path)
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
                    deck=data["deck"],
                    loot=data["loot"],
                    event_manager=event_manager
                )
        return prototypes

    def create_enemy(
            self, enemy_id, card_cache, status_registry, card_rewards
            ) -> Enemy:
        """
        Get a new Enemy using the given prototype id.
        """
        if enemy_id not in self.enemy_prototypes:
            raise KeyError(f"Enemy ID '{enemy_id}' not found.")
        prototype = self.enemy_prototypes[enemy_id]
        enemy = prototype.clone(card_cache, status_registry, card_rewards)
        return enemy

    def list_enemy_prototypes(self) -> list:
        """
        List all enemy prototype ids in the cache.
        """
        return list(self.enemy_prototypes.keys())
