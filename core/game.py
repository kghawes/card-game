from gameplay.combat_manager import CombatManager
from gameplay.town import Town
from core.registries import Registries
from core.cards import CardCache
from core.enemies import EnemyCache
from core.player import Player
from utils.text_interface import TextInterface
import utils.constants as constants

class Game:
    def __init__(self):
        self.text_interface = TextInterface()
        self.combat_manager = CombatManager()
        self.registries = Registries(constants.STATUSES_PATH, constants.ENCHANTMENTS_PATH)
        self.card_cache = CardCache(constants.CARD_PATHS, self.registries)
        self.enemy_cache = EnemyCache(constants.ENEMIES_PATH)
        self.registries.register_quests(constants.QUESTS_PATH, self.enemy_cache, self.card_cache)
        self.player = Player(self.card_cache, self.registries.statuses)
        self.town = Town()
        
    def game_loop(self):
        self.town.enter_town(self.text_interface)
        self.text_interface.send_message(constants.SPLASH_MESSAGE)
        self.player.name = "KK" #self.text_interface.name_prompt()
        
        for quest in self.registries.quests.quests:
            self.player.resources[constants.Resources.HEALTH.name].replenish()
            
            self.text_interface.send_message(quest.description)
    
            for encounter in quest.encounters:
                self.text_interface.send_message(encounter.enemy.name + " appeared! Entering combat!")
                self.combat_manager.do_combat(
                    self.player, encounter.enemy,
                    self.text_interface,
                    self.registries
                )
                if self.player.is_alive():
                    self.text_interface.send_message(constants.VICTORY_MESSAGE)
                    self.player.gain_gold(encounter.enemy.loot.gold)
                else:
                    self.text_interface.send_message(constants.DEFEAT_MESSAGE)
                    return
        
        self.text_interface.send_message(constants.BEAT_GAME_MESSAGE)
            