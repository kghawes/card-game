"""
This module defines the CardManager class.
"""
import random
from typing import Tuple
import utils.constants as c
from gameplay.library import Library

class CardManager:
    """
    This class handles the movement of cards between piles.
    """
    def __init__(self, starting_deck, card_cache, event_manager, effect_registry):
        """
        Initialize a new CardManager.
        """
        self.deck = self._create_deck(starting_deck, card_cache, effect_registry)
        self.hand = []
        self.discard_pile = []
        self.consumed_pile = []
        self.library = Library()
        self.event_manager = event_manager

    def _create_deck(self, deck_list, card_cache, effect_registry) -> list:
        """
        From a list of card ids, generate Card objects.
        """
        deck = []
        for entry in deck_list:
            card_id = entry.get("card")
            quantity = entry.get("quantity")
            for _ in range(quantity):
                deck.append(card_cache.create_card(card_id, effect_registry))
        return deck

    def try_add_to_deck(self, card) -> tuple[bool, bool, bool]:
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
            if not subject.is_enemy:
                self.event_manager.logger.log(
                    f"{subject.name} drew {card.name}.", True
                    )
        self.recalculate_for_new_card(subject, status_registry)

    def recalculate_for_new_card(self, subject, status_registry):
        """
        Recalculate modifiers and costs when a card is added to the hand.
        """
        modifier_manager = subject.modifier_manager
        modifier_manager.recalculate_all_costs(status_registry, self)
        modifier_manager.recalculate_all_effects(status_registry, self)
        status_manager = subject.status_manager
        levitate = status_manager.get_leveled_status(c.StatusNames.LEVITATE.name)
        if levitate is not None:
            levitate.reference.trigger_on_change(subject, levitate.get_level())

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

    def discard(self, card, subject, is_being_played=False):
        """
        Move the card from the hand to the discard pile, consumed pile, or
        deck.
        """
        if card not in self.hand:
            return
        status_manager = subject.status_manager

        card.reset_card()
        if card.matches(c.CardTypes.CONSUMABLE.name) and is_being_played:
            self.consumed_pile.insert(0, card)
            # TODO: log
        else:
            water_walking_id = c.StatusNames.WATER_WALKING.name
            if water_walking_id in status_manager.statuses and is_being_played:
                self.deck.insert(0, card) # TODO: log
            else:
                self.discard_pile.insert(0, card)
                self.event_manager.logger.log(
                    f"{subject.name} discarded {card.name}.", True
                    )
        self.hand.remove(card)

        levitate = status_manager.get_leveled_status(c.StatusNames.LEVITATE.name)
        if levitate is not None:
            levitate.reference.trigger_on_change(subject, levitate.get_level())

    def discard_random(self, quantity, subject):
        """
        Randomly discard up to the given quantity of cards.
        """
        while len(self.hand) > 0 and quantity > 0:
            card = random.choice(self.hand)
            self.discard(card, subject)
            quantity -= 1

    def discard_hand(self, subject):
        """
        Discard the hand after each turn.
        """
        while len(self.hand) > 0:
            self.discard(self.hand[0], subject)

    def undiscard(self, card_index, subject, status_registry):
        """
        Move a card from the discard pile to the hand.
        """
        hand_size = subject.modifier_manager.calculate_cards_to_draw()
        assert self.discard_pile and len(self.hand) < hand_size
        card = self.discard_pile.pop(card_index)
        self.hand.append(card)
        self.recalculate_for_new_card(subject, status_registry)

    def reset_cards(self):
        """
        Return cards to the deck at the end of combat.
        """
        self.deck.extend(self.consumed_pile)
        self.consumed_pile = []
        self.deck.extend(self.discard_pile)
        self.discard_pile = []
        self.deck.extend(self.hand)
        self.hand = []
        self.shuffle()
