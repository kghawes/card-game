"""
This module defines the Treasure class which represents rewards in game.
"""
import random
from utils.utils import load_json
import utils.constants as c

class Treasure:
    """
    This class represents rewards from a single encounter.
    """
    def __init__(self, treasure_data, card_rewards):
        """
        Initialize a new Treasure.
        """
        gold_range = treasure_data.get("gold")
        self.gold = random.randint(*gold_range)
        self.exp = treasure_data.get("exp")
        card_group_id = treasure_data.get("cards")
        self.cards = None # card_rewards[card_group_id]
        self.is_boss = True if c.BOSS_ID in card_group_id else False

    def select_cards(self, number_of_cards, player_class, card_cache) -> list:
        """
        Return a list of random cards from the card group.
        """
        pass
        # selection = []
        # choices = list(self.cards.items())
        # items, weights = zip(*choices)
        # while len(selection) < number_of_cards:
        #     card_id = random.choices(items, weights=weights, k=1)[0]
        #     card = card_cache.create_card(card_id)
        #     if card.matches(c.CardTypes.SKILL.name) \
        #         and not card.matches(
        #             c.ClassSpecializations[player_class].value
        #             ):
        #         continue
        #     selection.append(card)
        # return selection


class CardRewards:
    """
    This class holds the data for loot tables.
    """
    def __init__(self, path):
        """
        Initialize a new CardRewards.
        """
        self.card_groups = load_json(path)
