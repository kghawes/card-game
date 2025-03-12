"""
This module defines the CardManager class.
"""
import random
import utils.constants as c
from gameplay.library import Library

class CardManager:
    """
    This class handles the movement of cards between piles.
    """
    def __init__(self, starting_deck, card_cache, event_manager):
        """
        Initialize a new CardManager.
        """
        self.deck = self._create_deck(starting_deck, card_cache)
        self.hand = []
        self.discard_pile = []
        self.consumed_pile = []
        self.library = Library()
        self.event_manager = event_manager

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

    from typing import Tuple

    def try_add_to_deck(self, card) -> Tuple[bool, bool, bool]:
        """
        Attempt to add the card to the deck and return success flag and error
        message.
        """
        allowed = True
        too_many_copies = False
        too_many_cards = False
        card_frequency = 0
        for card_in_deck in self.deck:
            if card_in_deck.name == card.name:
                card_frequency += 1
        if card_frequency >= c.MAX_CARD_FREQUENCY:
            allowed = False
            too_many_copies = True
        if len(self.deck) >= c.MAX_DECK_SIZE:
            allowed = False
            too_many_cards = True
        if allowed:
            self.deck.append(card)
        return allowed, too_many_copies, too_many_cards

    def shuffle(self):
        """
        Randomize the order of cards in the deck.
        """
        random.shuffle(self.deck)

    def draw(self, subject, status_registry, cards_to_draw=1):
        """
        Draw the indicated number of cards, shuffling the discard pile back
        into the deck if necessary.
        """
        if cards_to_draw == 0:
            return
        while cards_to_draw > 0:
            if len(self.hand) >= c.MAX_HAND_SIZE:
                break
            if len(self.deck) == 0:
                self.deck = self.discard_pile[:]
                self.discard_pile = []
                self.shuffle()
                self.event_manager.dispatch('empty_discard_pile')
            if not self.deck:
                break
            card = self.deck.pop(0)
            self.hand.append(card)
            cards_to_draw -= 1
        self.recalculate_for_new_card(subject, status_registry)

    def recalculate_for_new_card(self, subject, status_registry):
        """
        Recalculate modifiers and costs when a card is added to the hand.
        """
        modifier_manager = subject.modifier_manager
        modifier_manager.recalculate_all_costs(status_registry, self)
        modifier_manager.recalculate_all_effects(status_registry, self)
        status_manager = subject.status_manager
        levitate = c.StatusNames.LEVITATE.name
        if status_manager.has_status(levitate, subject, status_registry):
            status_registry.get_status(levitate).trigger_on_change(
                subject, status_manager.get_status_level(levitate)
                )

    def draw_hand(self, subject, registries):
        """
        Draw the appropriate number of cards at the beginning of a turn.
        """
        cards_to_draw = subject.modifier_manager.calculate_cards_to_draw()

        # wb = c.StatusNames.WATER_BREATHING.name
        # if subject.status_manager.has_status(wb, subject, registries.statuses):
        #     wb_status = registries.statuses.get_status(wb)
        #     wb_level = subject.status_manager.get_status_level(wb)
        #     cards_to_draw -= wb_status.draw_from_discard(
        #         subject, wb_level, registries.statuses
        #         )

        self.draw(subject, registries.statuses, cards_to_draw)

        # ss = c.StatusNames.SWIFT_SWIM.name
        # if subject.status_manager.has_status(ss, subject, registries.statuses):
        #     ss_status = registries.statuses.get_status(ss)
        #     ss_level = subject.status_manager.get_status_level(ss)
        #     ss_status.do_redraw(
        #         subject, ss_level, registries
        #         )

    def discard(self, card, subject, status_registry, is_being_played=False):
        """
        Move the card from the hand to the discard pile, consumed pile, or
        deck.
        """
        if card not in self.hand:
            return

        card.reset_card()
        if card.matches(c.CardTypes.CONSUMABLE.name) and is_being_played:
            self.consumed_pile.insert(0, card)
        elif subject.status_manager.has_status(
                c.StatusNames.WATER_WALKING.name, subject, status_registry
                ) and is_being_played:
            self.deck.insert(0, card)
        else:
            self.discard_pile.insert(0, card)
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

    def undiscard(self, card_index, subject, status_registry):
        """
        Move a card from the discard pile to the hand.
        """
        hand_size = subject.modifier_manager.calculate_cards_to_draw()
        assert self.discard_pile and len(self.hand) < hand_size
        card = self.discard_pile.pop(card_index)
        self.hand.append(card)
        self.recalculate_for_new_card(subject, status_registry)

    def reset_consumed_cards(self):
        """
        Return cards from the consumed pile to the deck at the end of combat.
        """
        self.deck += self.consumed_pile
        self.consumed_pile = []
