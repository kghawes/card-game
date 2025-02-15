from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.graphics import Rectangle, Color
from kivy.vector import Vector
from kivy.properties import ObjectProperty, BooleanProperty, ColorProperty, StringProperty
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.config import Config
import gui_constants as constants

Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
Config.set('graphics', 'resizable', '0')

Builder.load_file('card.kv')

class PlayArea(Widget):
    pass

class CardPile(Widget):
    def show_cardback(self):
        cardback = Card({'type': 'CARD_BACK'})
        cardback.is_draggable = False
        cardback.center_x = self.center_x
        cardback.center_y = self.center_y
        self.add_widget(cardback)
        with cardback.canvas:
            Color(rgba=[1, 1, 1, 1])
            Rectangle(pos=cardback.pos, size=cardback.size, source='assets/cardback.png')

class AnimationLayer(FloatLayout):
    pass

class Hand(FloatLayout):
    def position_cards(self):
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
        self.add_widget(card, index=index)
        self.position_cards()
    
    def remove_from_hand(self, card):
        self.remove_widget(card)
        self.position_cards()

class Card(Widget):
    is_draggable = BooleanProperty(True)
    border_color = ColorProperty([0, 0, 0, 0])
    resource_cost_color = ColorProperty([0, 0, 0, 0])
    card_type = StringProperty('CARD_BACK')

    def __init__(self, card_data, **kwargs):
        super().__init__(**kwargs)
        self.click_location = (0, 0)
        self.starting_position = (self.center_x, self.center_y)
        self.hand_index = 0
        self.card_type = card_data['type']
        self.border_color = constants.CARD_TYPE_COLORS[self.card_type]['border']

    def on_touch_down(self, touch):
        if super().on_touch_down(touch):
            return True
        if not self.is_draggable or not self.collide_point(touch.x, touch.y):
            return False
        self.click_location = (touch.x, touch.y)
        self.starting_position = (self.center_x, self.center_y)
        touch.grab(self)
        self.hand_index = self.parent.children.index(self)
        animation_layer = self.parent.get_root_window().children[0].animation_layer
        hand = self.parent
        for card in hand.children:
            card.is_draggable = False
        hand.remove_from_hand(self)
        animation_layer.add_widget(self)
        return True

    def on_touch_move(self, touch):
        if touch.grab_current is self:
            offset = tuple(Vector(*touch.pos) - Vector(*self.click_location))
            new_position = tuple(Vector(*self.starting_position) + Vector(*offset))
            self.center_x = max(self.width / 2, min(new_position[0], Window.width - self.width / 2))
            self.center_y = max(self.height / 2, min(new_position[1], Window.height - self.height / 2))
            return True
        return False

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self)
            play_area = self.get_root_window().children[0].play_area
            if play_area.collide_point(self.center_x, self.center_y):
                self.center_x = play_area.center_x
                self.center_y = play_area.center_y
                Clock.schedule_once(self.move_to_discard, 1)
            else:
                hand = self.get_root_window().children[0].hand
                self.parent.remove_widget(self)
                hand.add_to_hand(self, index=self.hand_index)
                for card in hand.children:
                    card.is_draggable = True
            return True
        return False

    def move_to_discard(self, dt):
        discard_pile = self.get_root_window().children[0].discard_pile
        self.center_x = discard_pile.center_x
        self.center_y = discard_pile.center_y
        self.parent.remove_widget(self)
        if discard_pile.children:
            discard_pile.remove_widget(discard_pile.children[0])
        discard_pile.add_widget(self)
        self.is_draggable = False
        hand = self.get_root_window().children[0].hand
        for card in hand.children:
            card.is_draggable = True

class CardGame(Widget):
    play_area = ObjectProperty(None)
    hand = ObjectProperty(None)
    deck = ObjectProperty(None)
    discard_pile = ObjectProperty(None)
    animation_layer = ObjectProperty(None)

    def end_turn(self):
        pass

class CardGameApp(App):
    def build(self):
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
