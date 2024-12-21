import random

class CardManager:
    def __init__(self, starting_deck, card_cache):
        self.deck = self._create_deck(starting_deck, card_cache)
        self.hand = []
        self.discard_pile = []
    
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

    def draw(self, cards_to_draw=6):
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
        
    def reset_effect_levels(self):
        for card in self.deck:
            for effect_level in card.effects.values():
                effect_level.reset()