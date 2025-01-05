"""
This module defines the CardManager class.
"""
import random
import utils.constants as c

class CardManager:
    """This class handles the movement of cards between piles."""
    def __init__(self, starting_deck, card_cache):
        """Initialize a new CardManager."""
        self.deck = self._create_deck(starting_deck, card_cache)
        self.hand = []
        self.discard_pile = []

    def _create_deck(self, deck_list, card_cache) -> list:
        """From a list of card ids, generate Card objects."""
        deck = []
        for entry in deck_list:
            card_id = entry.get("card")
            quantity = entry.get("quantity")
            for _ in range(quantity):
                deck.append(card_cache.create_card(card_id))
        return deck

    def shuffle(self):
        """Randomize the order of cards in the deck."""
        random.shuffle(self.deck)

    def draw(self, cards_to_draw=1) -> bool:
        """Draw the indicated number of cards, shuffling the discard
        pile back into the deck if necessary. Return False if the max
        hand size was met or True if all cards were able to be drawn."""
        while cards_to_draw > 0:
            if len(self.hand) == c.MAX_HAND_SIZE:
                return False
            if len(self.deck) == 0:
                self.deck = self.discard_pile[:]
                self.discard_pile = []
                self.shuffle()
            if not self.deck:
                break
            card = self.deck.pop(0)
            self.hand.append(card)

            # Recalculate modifiers for newly drawn cards
            card.reset_card()
            cards_to_draw -= 1
        return True

    def draw_hand(self, modifier_manager):
        """Draw the appropriate number of cards at the beginning of a
        turn."""
        self.draw(modifier_manager.calculate_cards_to_draw())

    def discard(self, card):
        """Move the card from the hand to the discard pile."""
        # Reset modifiers when discarding
        card.reset_card()
        self.discard_pile.append(card)
        self.hand.remove(card)

    def discard_random(self, quantity):
        """Randomly discard up to the given quantity of cards."""
        while len(self.hand) > 0 and quantity > 0:
            card = random.choice(self.hand)
            self.discard(card)
            quantity -= 1

    def discard_hand(self):
        """Discard the hand after each turn."""
        while len(self.hand) > 0:
            self.discard(self.hand[0])
