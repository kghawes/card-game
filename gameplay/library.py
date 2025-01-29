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
            deck.sort(key=lambda card: card.name)
            self.stored_cards.sort(key=lambda card: card.name)
            menu_choice = text_interface.library_options_prompt()
            if menu_choice == 0:  # show deck
                cards = self.handle_storage_menu(
                    deck, deck, text_interface, effect_registry, False
                    )
                if cards:
                    self.deposit_cards(cards, deck)
            elif menu_choice == 1:  # show stored cards
                cards = self.handle_storage_menu(
                    self.stored_cards, deck, text_interface, effect_registry,
                    True
                    )
                if cards:
                    self.withdraw_cards(cards, deck)
            elif menu_choice == 2:  # exit to town
                return
            else:
                assert False

    def handle_storage_menu(
            self, storage, deck, text_interface, effect_registry, is_storage
            ):
        """
        Handles the logic for displaying and selecting cards from the deck or
        storage.
        Returns a list of cards to deposit or withdraw.
        """
        selected_indices = text_interface.storage_options_prompt(
            storage, is_storage
            )
        if not selected_indices or selected_indices[0] == -1:
            return []  # Exit to library

        cards = [storage[index] for index in selected_indices]

        if is_storage:
            can_modify = (len(deck) + len(cards)) <= c.MAX_DECK_SIZE
        else:
            can_modify = (len(deck) - len(cards)) >= c.MIN_DECK_SIZE

        if text_interface.display_library_cards(
                cards, can_modify, is_storage, effect_registry
                ):
            return cards
        return []

    def deposit_cards(self, cards, deck):
        """
        Move the card from the deck to the library.
        """
        for card in cards:
            if card not in deck:
                raise ValueError("Card is not in deck.")
            if len(deck) <= c.MIN_DECK_SIZE:
                raise ValueError(
                    f"Deck cannot have fewer than {c.MIN_DECK_SIZE} cards."
                    )
            deck.remove(card)
            self.stored_cards.append(card)

    def withdraw_cards(self, cards, deck):
        """
        Move the card from the library to the deck.
        """
        for card in cards:
            if card not in self.stored_cards:
                raise ValueError("Card is not in library.")
            if len(deck) >= c.MAX_DECK_SIZE:
                raise ValueError(
                    f"Deck cannot have more than {c.MAX_DECK_SIZE} cards."
                    )
            self.stored_cards.remove(card)
            deck.append(card)
