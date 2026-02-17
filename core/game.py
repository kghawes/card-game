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
from utils.debug_tools import DebugTools

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
        self.registries = Registries(
            c.EFFECTS_PATH, c.STATUSES_PATH, c.ENCHANTMENTS_PATH, \
                c.ATTRIBUTES_PATH, self.event_manager
            )
        self.card_cache = CardCache(c.CARD_PATHS, self.registries)
        self.enemy_cache = EnemyCache(c.ENEMIES_PATHS, self.event_manager)
        self.card_rewards = CardRewards(c.CARD_REWARDS_PATH)
        self.registries.register_quests(
            c.QUESTS_PATH, c.ENEMY_GROUPS_PATH, self.enemy_cache,
            self.card_cache, self.card_rewards.card_groups
            )
        self.player = Player(
            self.card_cache, self.registries,
            c.ClassSpecializations.FIGHTER.name, self.event_manager
            )
        self.player.name = "Player"
        self.town = Town()
        self.debug_tools = DebugTools(self.event_manager, self.registries)

    def start_game(self):
        """
        Start the game.
        """
        self.town.enter_town()
        self.event_manager.dispatch('start_game')

    def start_quest(self):
        """
        Start the next quest.
        """
        self.quest = self.registries.quests.quests.pop(0)
        health = self.player.resources[c.Resources.HEALTH.name]
        health.replenish(self.player.modifier_manager)
        self.event_manager.dispatch('start_quest', self.quest)

    def start_encounter(self):
        """Start the next encounter."""
        encounter = self.quest.encounters.pop(0)
        self.enemy = encounter.enemy
        self.combat_manager.start_combat(self.player, self.enemy)
