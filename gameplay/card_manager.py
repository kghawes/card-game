"""
This module defines the CardManager class.
"""
import random
import utils.constants as c

class CardManager:
    """
    This class handles the movement of cards between piles.
    """
    def __init__(self, starting_deck, card_cache):
        """
        Initialize a new CardManager.
        """
        self.deck = self._create_deck(starting_deck, card_cache)
        self.hand = []
        self.discard_pile = []
        self.consumed_pile = []

    def _create_deck(self, deck_list, card_cache) -> list:
        """
        From a list of card ids, generate Card objects.
        """
        deck = []
        for entry in deck_list:
            card_id = entry.get("card")
            quantity = entry.get("quantity")
            for _ in range(quantity):
                deck.append(card_cache.create_card(card_id))
        return deck

    def shuffle(self):
        """
        Randomize the order of cards in the deck.
        """
        random.shuffle(self.deck)

    def draw(self, subject, status_registry, cards_to_draw=1) -> bool:
        """
        Draw the indicated number of cards, shuffling the discard pile back
        into the deck if necessary. Return False if the max hand size was met
        or True if all cards were able to be drawn.
        """
        while cards_to_draw > 0:
            if len(self.hand) >= c.MAX_HAND_SIZE:
                break
            if len(self.deck) == 0:
                self.deck = self.discard_pile[:]
                self.discard_pile = []
                self.shuffle()
            if not self.deck:
                break
            card = self.deck.pop(0)
            self.hand.append(card)
            cards_to_draw -= 1

        modifier_manager = subject.modifier_manager
        modifier_manager.recalculate_all_costs(status_registry, self)
        modifier_manager.recalculate_all_effects(status_registry, self)
        status_manager = subject.status_manager
        levitate = c.StatusNames.LEVITATE.name
        if status_manager.has_status(levitate, subject, status_registry):
            status_registry.get_status(levitate).trigger_on_change(
                subject, status_manager.get_status_level(levitate)
                )

    def draw_hand(self, subject, status_registry):
        """
        Draw the appropriate number of cards at the beginning of a turn.
        """
        self.draw(
            subject, status_registry,
            subject.modifier_manager.calculate_cards_to_draw()
            )

    def discard(self, card, subject, status_registry):
        """
        Move the card from the hand to the discard pile.
        """
        if card not in self.hand:
            return
        
        card.reset_card()
        if card.matches(c.CardTypes.CONSUMABLE.name):
            self.consumed_pile.append(card)
        else:
            self.discard_pile.append(card)
        self.hand.remove(card)
        
        status_manager = subject.status_manager
        levitate = c.StatusNames.LEVITATE.name
        if status_manager.has_status(levitate, subject, status_registry):
            status_registry.get_status(levitate).trigger_on_change(
                subject, status_manager.get_status_level(levitate)
                )

    def discard_random(self, quantity, subject, status_registry):
        """
        Randomly discard up to the given quantity of cards.
        """
        while len(self.hand) > 0 and quantity > 0:
            card = random.choice(self.hand)
            self.discard(card, subject, status_registry)
            quantity -= 1

    def discard_hand(self, subject, status_registry):
        """
        Discard the hand after each turn.
        """
        while len(self.hand) > 0:
            self.discard(self.hand[0], subject, status_registry)

    def reset_consumed_cards(self):
        """
        Return cards from the consumed pile to the deck at the end of combat.
        """
        self.deck += self.consumed_pile
        self.consumed_pile = []
