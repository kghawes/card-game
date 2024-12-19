from gameplay.combat_manager import CombatManager
from gameplay.quests import QuestRegistry
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
        self.registries = Registries(constants.EFFECTS_PATH, constants.STATUSES_PATH, constants.ENCHANTMENTS_PATH)
        self.combat_manager = CombatManager()
        self.card_cache = CardCache(constants.CARD_PATHS, self.registries)
        self.enemy_cache = EnemyCache(constants.ENEMIES_PATH)
        self.quest_registry = QuestRegistry(constants.QUESTS_PATH, self.enemy_cache, self.card_cache)
        self.player = Player(self.card_cache)
        self.town = Town()
        
    def game_loop(self):
        self.town.enter_town(self.text_interface)
        self.text_interface.send_message(constants.SPLASH_MESSAGE)
        self.player.name = "KK" #self.text_interface.name_prompt()
        
        for quest in self.quest_registry.quests:
            self.player.replenish_health()
            
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
            