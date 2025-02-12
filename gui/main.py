from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.properties import ObjectProperty, BooleanProperty
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.config import Config

Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
Config.set('graphics', 'resizable', '0')

class PlayArea(Widget):
    pass

class CardPile(Widget):
    pass

class HeldCardLayer(FloatLayout):
    pass

class Card(Widget):
    is_draggable = BooleanProperty(True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.click_location = (0, 0)
        self.starting_position = (self.center_x, self.center_y)
        self.hand_index = 0

    def on_touch_down(self, touch):
        if super().on_touch_down(touch):
            return True
        if not self.is_draggable or not self.collide_point(touch.x, touch.y):
            return False
        self.click_location = (touch.x, touch.y)
        self.starting_position = (self.center_x, self.center_y)
        touch.grab(self)
        self.hand_index = self.parent.children.index(self)
        held_card_layer = self.parent.get_root_window().children[0].held_card_layer
        self.parent.remove_widget(self)
        held_card_layer.add_widget(self)
        return True

    def on_touch_move(self, touch):
        if touch.grab_current is self:
            offset_x = touch.x - self.click_location[0]
            offset_y = touch.y - self.click_location[1]
            new_x = self.starting_position[0] + offset_x
            new_y = self.starting_position[1] + offset_y
            self.center_x = max(self.width / 2, min(new_x, Window.width - self.width / 2))
            self.center_y = max(self.height / 2, min(new_y, Window.height - self.height / 2))
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
                hand.add_widget(self, index=self.hand_index)
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
        self.is_grabbed = False

class Hand(BoxLayout):
    pass

class CardGame(Widget):
    play_area = ObjectProperty(None)
    hand = ObjectProperty(None)
    discard_pile = ObjectProperty(None)
    held_card_layer = ObjectProperty(None)

class CardGameApp(App):
    def build(self):
        game = CardGame()
        card1 = Card()
        card1_label = Label(text="Card 1", size_hint=(None, None))
        card1.bind(pos=lambda instance, value: card1_label.setter('pos')(card1, (card1.center_x - card1_label.width / 2, card1.center_y - card1_label.height / 2)))
        card1.add_widget(card1_label)
        
        card2 = Card()
        card2_label = Label(text="Card 2", size_hint=(None, None))
        card2.bind(pos=lambda instance, value: card2_label.setter('pos')(card2, (card2.center_x - card2_label.width / 2, card2.center_y - card2_label.height / 2)))
        card2.add_widget(card2_label)
        
        card3 = Card()
        card3_label = Label(text="Card 3", size_hint=(None, None))
        card3.bind(pos=lambda instance, value: card3_label.setter('pos')(card3, (card3.center_x - card3_label.width / 2, card3.center_y - card3_label.height / 2)))
        card3.add_widget(card3_label)
        game.hand.add_widget(card1)
        game.hand.add_widget(card2)
        game.hand.add_widget(card3)
        
        return game

if __name__ == '__main__':
    CardGameApp().run()
