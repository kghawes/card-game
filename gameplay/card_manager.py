import random
import utils.constants as constants

class CardManager:
    def __init__(self, starting_deck, card_cache):
        self.deck = self._create_deck(starting_deck, card_cache)
        self.hand = []
        self.discard_pile = []
        self.cards_to_draw = constants.HAND_SIZE

    def _create_deck(self, deck_list, card_cache):
        deck = []
        for entry in deck_list:
            card_id = entry.get("card")
            quantity = entry.get("quantity")
            for _ in range(quantity):
                deck.append(card_cache.create_card(card_id))
        return deck

    def shuffle(self):
        random.shuffle(self.deck)

    def draw(self, cards_to_draw=1) -> bool:
        while cards_to_draw > 0:
            if len(self.hand) == constants.MAX_HAND_SIZE:
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
        return self.draw(self.cards_to_draw)

    def discard(self, card):
        # Reset modifiers when discarding
        card.reset_card()
        self.discard_pile.append(card)
        self.hand.remove(card)

    def discard_hand(self):
        for card in self.hand:
            self.discard(card)

    def reset_cards_to_draw(self):
        self.cards_to_draw = constants.HAND_SIZE
