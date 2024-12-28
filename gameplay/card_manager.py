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
        self.cards_to_draw = c.HAND_SIZE

    def _create_deck(self, deck_list, card_cache):
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
        pile back into the deck if necessary."""
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

    def draw_hand(self) -> bool:
        """Draw a hand of cards each turn."""
        return self.draw(self.cards_to_draw)

    def discard(self, card):
        """Move the card from the hand to the discard pile."""
        # Reset modifiers when discarding
        card.reset_card()
        self.discard_pile.append(card)
        self.hand.remove(card)

    def discard_hand(self):
        """Discard the hand after each turn."""
        while len(self.hand) > 0:
            self.discard(self.hand[0])

    def reset_cards_to_draw(self):
        """Reset the hand size to its base value."""
        self.cards_to_draw = c.HAND_SIZE
