from gameplay.combat_manager import CombatManager
from cards import CardCache
from player import Player
import utils.constants as constants

class Game:
    def __init__(self):
        self.combat_manager = CombatManager()
        self.card_cache = CardCache(constants.CARDS_PATH)
        self.player = Player()
    def game_loop():
        player = Player("", STARTING_DECK)
        enemy = Enemy("Cliff Racer", 9, 4, E_CLIFFRACER_DECK, Treasure(2))
        quest = Quest("Embarking on a test quest.", Encounter(enemy))
        text_interface = TextInterface()
        combat_manager = CombatManager()

        text_interface.send_message(M_SPLASH)
        player.name = text_interface.name_prompt()
        text_interface.send_message(quest.description)
        text_interface.send_message(quest.encounter.enemy.name + " appeared! Entering combat!")

        if combat_manager.do_combat(player, enemy, text_interface):
            text_interface.send_message(M_VICTORY)
            player.gain_gold(quest.encounter.enemy.loot.gold)
        else:
            text_interface.send_message(M_DEFEAT)