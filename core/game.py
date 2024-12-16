from gameplay.combat_manager import CombatManager
from gameplay.quests import QuestCache
from gameplay.town import Town
from core.effects import EffectRegistry
from core.statuses import StatusRegistry
from core.cards import CardCache
from core.enemies import EnemyCache
from core.player import Player
from utils.text_interface import TextInterface
import utils.constants as constants

class Game:
    def __init__(self):
        self.text_interface = TextInterface()
        self.effect_registry = EffectRegistry()
        self.status_registry = StatusRegistry()
        self.card_cache = CardCache(constants.CARDS_PATH)
        self.enemy_cache = EnemyCache(constants.ENEMIES_PATH, self.card_cache)
        self.quest_cache = QuestCache(constants.QUESTS_PATH, self.enemy_cache)
        self.player = Player(self.card_cache)
        self.town = Town()
        
    def game_loop(self):
        self.town.enter_town(self.text_interface)
        self.text_interface.send_message(constants.SPLASH_MESSAGE)
        self.player.name = self.text_interface.name_prompt()
        
        for quest in self.quest_cache.quests:
            self.player.replenish_health()
            
            self.text_interface.send_message(quest.description)
    
            for encounter in quest.encounters:
                self.text_interface.send_message(encounter.enemy.name + " appeared! Entering combat!")
                if CombatManager().do_combat(self.player, encounter.enemy, self.text_interface, self.status_registry):
                    self.text_interface.send_message(constants.VICTORY_MESSAGE)
                    self.player.gain_gold(encounter.enemy.loot.gold)
                else:
                    self.text_interface.send_message(constants.DEFEAT_MESSAGE)
                    return
        
        self.text_interface.send_message(constants.BEAT_GAME_MESSAGE)
            