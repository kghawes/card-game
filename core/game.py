from gameplay.combat_manager import CombatManager
from gameplay.quests import Quest
from gameplay.encounters import Encounter
from core.cards import CardCache
from core.enemies import EnemyCache
from core.player import Player
from utils.text_interface import TextInterface
import utils.constants as constants

class Game:
    def __init__(self):
        self.combat_manager = CombatManager()
        self.text_interface = TextInterface()
        self.card_cache = CardCache(constants.CARDS_PATH)
        self.enemy_cache = EnemyCache(constants.ENEMIES_PATH, self.card_cache)
        self.player = Player(self.card_cache)
        
    def game_loop(self):
        enemy = self.enemy_cache.create_enemy("CLIFF_RACER")
        quest = Quest("Embarking on a test quest.", Encounter(enemy))

        self.text_interface.send_message(constants.SPLASH_MESSAGE)
        self.player.name = self.text_interface.name_prompt()
        self.text_interface.send_message(quest.description)
        self.text_interface.send_message(quest.encounter.enemy.name + " appeared! Entering combat!")

        if self.combat_manager.do_combat(self.player, enemy, self.text_interface):
            self.text_interface.send_message(constants.VICTORY_MESSAGE)
            self.player.gain_gold(quest.encounter.enemy.loot.gold)
        else:
            self.text_interface.send_message(constants.DEFEAT_MESSAGE)