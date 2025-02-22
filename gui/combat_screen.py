"""Combat Screen Module for Card Game"""
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.graphics import Rectangle, Color, RoundedRectangle
from kivy.vector import Vector
from kivy.properties import ObjectProperty, BooleanProperty, ColorProperty, StringProperty, NumericProperty
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.config import Config
import gui_constants as constants
from card import Card

Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
Config.set('graphics', 'resizable', '0')

Builder.load_file('card.kv')


class PlayArea(Widget):
    """Widget representing the play area where cards can be played."""
    pass


class CardPile(Widget):
    """Widget representing a pile of cards."""

    def show_cardback(self):
        """Displays the back of a card."""
        cardback = Card({'type': 'CARD_BACK'})
        cardback.is_draggable = False
        cardback.center_x = self.center_x
        cardback.center_y = self.center_y
        self.add_widget(cardback)
        with cardback.canvas:
            Color(rgba=[1, 1, 1, 1])
            Rectangle(pos=cardback.pos, size=cardback.size, source='assets/cardback.png')


class AnimationLayer(FloatLayout):
    """Layer for handling animations or widgets that need to be temporarily on top of the z-stack."""
    pass


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
        card1 = Card({'type': 'WEAPON'})
        card1_label = Label(text="Card 1", size_hint=(None, None))
        card1.bind(pos=lambda instance, value: card1_label.setter('pos')(card1, (card1.center_x - card1_label.width / 2, card1.center_y - card1_label.height / 2)))
        card1.add_widget(card1_label)
        card2 = Card({'type': 'ARMOR'})
        card2_label = Label(text="Card 2", size_hint=(None, None))
        card2.bind(pos=lambda instance, value: card2_label.setter('pos')(card2, (card2.center_x - card2_label.width / 2, card2.center_y - card2_label.height / 2)))
        card2.add_widget(card2_label)
        card3 = Card({'type': 'SPELL'})
        card3_label = Label(text="Card 3", size_hint=(None, None))
        card3.bind(pos=lambda instance, value: card3_label.setter('pos')(card3, (card3.center_x - card3_label.width / 2, card3.center_y - card3_label.height / 2)))
        card3.add_widget(card3_label)
        game.hand.add_widget(card1)
        game.hand.add_widget(card2)
        game.hand.add_widget(card3)
        game.hand.add_widget(Card({'type': 'SKILL'}))
        game.hand.add_widget(Card({'type': 'ITEM'}))
        game.hand.add_widget(Card({'type': 'CONSUMABLE'}))
        game.hand.add_widget(Card({'type': 'SPELL'}))
        game.hand.position_cards()
        game.deck.show_cardback()
        return game

CardGameApp().run()
