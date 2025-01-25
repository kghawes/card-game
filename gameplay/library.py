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

    def open_library(self, text_interface):
        """
        Show the library options screen.
        """
        text_interface.library_options_prompt()

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
