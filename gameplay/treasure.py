"""
This module defines the Treasure class which represents rewards in game.
"""
import random
import utils.utils.load_json as load_json
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
        card_group = card_rewards[card_group_id]
        is_boss = False
        if c.BOSS_ID in card_group_id:
            is_boss = True
        self.cards = self.select_card(card_group, is_boss)

    def select_card(card_group, is_boss) -> list:
        """
        Return a list of random cards from the card group based on their
        probabilities.
        """
        number_of_cards = c.NORMAL_CARD_REWARD
        choices = list(card_group.items())
        if is_boss:
            number_of_cards = c.BOSS_CARD_REWARD
        items, weights = zip(*choices)
        return random.choices(items, weights=weights, k=number_of_cards)


class CardRewards:
    def __init__(self):
        self.card_groups = load_json(c.CARD_REWARDS_PATH)