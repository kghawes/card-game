"""
This module defines the Library class.
"""
import utils.constants as c

class Library:
    """
    This class represents the card storage and deck editing system.
    """
    def __init__(self):
        """
        Initialize a new Library.
        """
        self.stored_cards = []

    def open_library(self, deck, text_interface, effect_registry):
        """
        Show the library options screen.
        """
        while True:
            menu_choice = text_interface.library_options_prompt(
                c.LIBRARY_OPTIONS
                )
            if menu_choice == 0:  # show deck
                selected_index = text_interface.storage_options_prompt(
                    deck, False
                    )
                if selected_index == -1:  # exit to library
                    continue
                card = deck[selected_index]
                can_deposit = len(deck) > c.MIN_DECK_SIZE
                if text_interface.display_library_card(
                    card, can_deposit, False, effect_registry
                    ):
                    self.deposit_card(card, deck)
            elif menu_choice == 1:  # show stored cards
                selected_index = text_interface.storage_options_prompt(
                    self.stored_cards, True
                    )
                if selected_index == -1:  # exit to library
                    continue
                card = self.stored_cards[selected_index]
                can_withdraw = len(deck) < c.MAX_DECK_SIZE
                if text_interface.display_library_card(
                    card, can_withdraw, True, effect_registry
                    ):
                    self.withdraw_card(card, deck)
            elif menu_choice == 2:  # exit library
                return
            else:
                assert False

    def deposit_card(self, card, deck):
        """
        Move the card from the deck to the library.
        """
        if card not in deck:
            raise ValueError("Card is not in deck.")
        if len(deck) <= c.MIN_DECK_SIZE:
            raise ValueError(
                f"Cannot have fewer than {c.MIN_DECK_SIZE} cards in your deck."
                )
        deck.remove(card)
        self.stored_cards.append(card)

    def withdraw_card(self, card, deck):
        """
        Move the card from the library to the deck.
        """
        if card not in self.stored_cards:
            raise ValueError("Card is not in library.")
        if len(deck) >= c.MAX_DECK_SIZE:
            raise ValueError(
                f"Cannot have more than {c.MAX_DECK_SIZE} cards in your deck."
                )
        self.stored_cards.remove(card)
        deck.append(card)
