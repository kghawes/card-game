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
from utils.text_interface import TextInterface
import utils.constants as c

class Game:
    """
    Holds the data needed for the game.
    """
    def __init__(self):
        """
        Initialize a new Game.
        """
        self.text_interface = TextInterface()
        self.combat_manager = CombatManager()
        self.registries = Registries(c.STATUSES_PATH, c.ENCHANTMENTS_PATH)
        self.card_cache = CardCache(c.CARD_PATHS, self.registries)
        self.enemy_cache = EnemyCache(c.ENEMIES_PATHS)
        self.card_rewards = CardRewards(c.CARD_REWARDS_PATH)
        self.registries.register_quests(
            c.QUESTS_PATH, c.ENEMY_GROUPS_PATH, self.enemy_cache,
            self.card_cache, self.card_rewards.card_groups
            )
        self.player = Player(
            self.card_cache, self.registries.statuses,
            c.ClassSpecializations.FIGHTER.name
            )
        self.town = Town()

    def game_loop(self):
        """
        Run the game.
        """
        self.text_interface.send_message(c.SPLASH_MESSAGE)
        self.player.name = "KK" #self.text_interface.name_prompt()

        #***************************CARD**ANALYSIS****************************#
        weapons = []
        armors = []
        combat_skills = []
        stealth_skills = []
        magic_skills = []
        skills = []
        alterations = []
        destructions = []
        illusions = []
        mysticisms = []
        restorations = []
        spells = []
        items = []
        consumables = []
        for card in self.card_cache.card_prototypes.values():
            if card.value == 0:
                continue
            if card.card_type == c.CardTypes.WEAPON.name:
                weapons.append(card)
                continue
            if card.card_type == c.CardTypes.ARMOR.name:
                armors.append(card)
                continue
            if card.card_type == c.CardTypes.ITEM.name:
                items.append(card)
                continue
            if card.card_type == c.CardTypes.CONSUMABLE.name:
                consumables.append(card)
                continue
            if card.card_type == c.CardTypes.SKILL.name:
                skills.append(card)
                if card.subtype == c.CardSubtypes.COMBAT.name:
                    combat_skills.append(card)
                    continue
                if card.subtype == c.CardSubtypes.STEALTH.name:
                    stealth_skills.append(card)
                    continue
                if card.subtype == c.CardSubtypes.MAGIC.name:
                    magic_skills.append(card)
                    continue
            if card.card_type == c.CardTypes.SPELL.name:
                spells.append(card)
                if card.subtype == c.CardSubtypes.ALTERATION.name:
                    alterations.append(card)
                    continue
                if card.subtype == c.CardSubtypes.DESTRUCTION.name:
                    destructions.append(card)
                    continue
                if card.subtype == c.CardSubtypes.ILLUSION.name:
                    illusions.append(card)
                    continue
                if card.subtype == c.CardSubtypes.MYSTICISM.name:
                    mysticisms.append(card)
                    continue
                if card.subtype == c.CardSubtypes.RESTORATION.name:
                    restorations.append(card)
        #*********************************************************************#

        for quest in self.registries.quests.quests:
            self.town.enter_town(##############################################
                self.player, self.text_interface, self.registries.effects######
                )##############################################################

            health = self.player.resources[c.Resources.HEALTH.name]
            health.replenish(self.player.modifier_manager)

            self.text_interface.send_message(quest.description)

            for encounter in quest.encounters:
                self.text_interface.send_message(
                    encounter.enemy.name + " appeared! Entering combat!"
                    )
                self.combat_manager.do_combat(
                    self.player, encounter.enemy,
                    self.text_interface,
                    self.registries,
                    self.card_cache
                )
                if not self.player.is_alive():
                    self.text_interface.send_message(c.DEFEAT_MESSAGE)
                    return

            self.town.enter_town(
                self.player, self.text_interface, self.registries.effects
                )

        self.text_interface.send_message(c.BEAT_GAME_MESSAGE)
