"""
This module contains the game data and game loop.
"""
from gameplay.combat_manager import CombatManager
from gameplay.town import Town
from core.registries import Registries
from core.player import Player
from utils.constants import ClassSpecializations, Resources
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
        self.registries = Registries(self.event_manager)

        default_class = ClassSpecializations.FIGHTER.name
        default_name = "Player"
        self.player = Player(self.registries, default_class, self.event_manager)
        self.player.name = default_name
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
        health = self.player.resources[Resources.HEALTH.name]
        health.replenish(self.player.modifier_manager)
        self.event_manager.dispatch('start_quest', self.quest)

    def start_encounter(self):
        """Start the next encounter."""
        encounter = self.quest.encounters.pop(0)
        self.enemy = encounter.enemy
        self.combat_manager.start_combat(self.player, self.enemy)
