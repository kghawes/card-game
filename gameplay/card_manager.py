import random

class CardManager:
    def __init__(self, starting_deck):
        self.deck = starting_deck[:]
        self.hand = []
        self.discard_pile = []

    def shuffle(self):
        random.shuffle(self.deck)

    def draw(self):
        cards_to_draw = 6
        while cards_to_draw > 0:
            if len(self.deck) == 0:
                self.deck = self.discard_pile[:]
                self.discard_pile = []
                self.shuffle()
            if not self.deck:
                break
            self.hand.append(self.deck.pop(0))
            cards_to_draw -= 1

    def discard(self, card):
        self.discard_pile.append(card)
        self.hand.remove(card)

    def discard_hand(self):
        self.discard_pile.extend(self.hand)
        self.hand = []