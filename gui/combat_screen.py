"""Combat Screen Module for Card Game"""
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ObjectProperty
from kivy.lang import Builder
from kivy.config import Config
import gui_constants as constants
from card import Card

Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
Config.set('graphics', 'resizable', '0')
Builder.load_file('card.kv')

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


class CardGame(Widget):
    """Main widget for the card game."""
    play_area = ObjectProperty(None)
    hand = ObjectProperty(None)
    deck = ObjectProperty(None)
    discard_pile = ObjectProperty(None)
    animation_layer = ObjectProperty(None)

    def end_turn(self):
        """Ends the current turn."""
        pass

class CardGameApp(App):
    """Main application class for the card game."""
    
    def build(self):
        """Builds the card game application."""
        game = CardGame()
        test_card = Card({
            'type': 'WEAPON',
            'subtype': 'Long Blade',
            'name': 'Iron Longsword',
            'id': 1,
            'cost': '3',
            'effects': {
                'Physical Damage Target': 2
                }
            })
        game.hand.add_widget(test_card)
        game.hand.position_cards()
        return game

CardGameApp().run()
