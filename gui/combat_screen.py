"""Combat Screen Module for Card Game"""
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ObjectProperty, BooleanProperty
import gui_constants as constants
from card import Card

class Hand(FloatLayout):
    """Widget representing the player's hand of cards."""

    def position_cards(self):
        """Positions the cards in the hand."""
        cards = self.children
        x = self.center_x
        y = self.center_y
        if len(cards) <= 5:
            for i, card in enumerate(cards):
                center_index = len(cards) // 2
                card.center_x = x + (i - center_index) * 208 + 104 * (1 - len(cards) % 2)
                card.center_y = y
        else:
            for i, card in enumerate(cards):
                card.center_x = i * (832 / (len(cards) - 1)) + 334
                card.center_y = y
    
    def add_to_hand(self, card, index=0):
        """Adds a card to the hand and repositions the cards."""
        self.add_widget(card, index=index)
        self.position_cards()
    
    def remove_from_hand(self, card):
        """Removes a card from the hand and repositions the cards."""
        self.remove_widget(card)
        self.position_cards()


class CombatScreen(Widget):
    """Widget representing the combat screen of the card game."""
    play_area = ObjectProperty(None)
    hand = ObjectProperty(Hand)
    deck = ObjectProperty(None)
    discard_pile = ObjectProperty(None)
    animation_layer = ObjectProperty(None)
    show_deck = BooleanProperty(True)

    def load(self):
        test_card = Card({
            'type': 'WEAPON',
            'subtype': 'Long Blade',
            'name': 'Iron Longsword',
            'id': 1,
            'cost': '3',
            'effects': {
                'Physical Damage Target': 2
                }
            }, self.animation_layer, self.hand, self.play_area, self.discard_pile)
        self.hand.add_widget(test_card)
        self.hand.position_cards()

    def end_turn(self):
        """Ends the current turn."""
        self.load() #pass
