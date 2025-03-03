"""
This module contains the game data and game loop.
"""
from gameplay.combat_manager import CombatManager
from gameplay.town import Town
from gameplay.treasure import CardRewards
from core.registries import Registries
from core.cards import CardCache
from core.enemies import EnemyCache
from core.player import Player
import utils.constants as c

class Game:
    """
    Holds the data needed for the game.
    """
    def __init__(self, event_manager):
        """
        Initialize a new Game.
        """
        self.event_manager = event_manager
        self.combat_manager = CombatManager(self.event_manager)
        self.registries = Registries(c.STATUSES_PATH, c.ENCHANTMENTS_PATH)
        self.card_cache = CardCache(c.CARD_PATHS, self.registries)
        self.enemy_cache = EnemyCache(c.ENEMIES_PATHS, self.event_manager)
        self.card_rewards = CardRewards(c.CARD_REWARDS_PATH)
        self.registries.register_quests(
            c.QUESTS_PATH, c.ENEMY_GROUPS_PATH, self.enemy_cache,
            self.card_cache, self.card_rewards.card_groups
            )
        self.player = Player(
            self.card_cache, self.registries.statuses,
            c.ClassSpecializations.FIGHTER.name, self.event_manager
            )
        self.town = Town()

    def game_loop(self):
        """
        Run the game.
        """
        self.town.enter_town(self.player, self.registries.effects)

        for quest in self.registries.quests.quests:
            health = self.player.resources[c.Resources.HEALTH.name]
            health.replenish(self.player.modifier_manager)

            for encounter in quest.encounters:
                self.combat_manager.do_combat(
                    self.player,
                    encounter.enemy,
                    self.registries,
                    self.card_cache
                )
                if not self.player.is_alive():
                    return

            self.town.enter_town(self.player, self.registries.effects)
