from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import (
    ObjectProperty, BooleanProperty
)
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.config import Config

Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

class PlayArea(Widget):
    pass

class Card(Widget):
    is_grabbed = BooleanProperty(False)
    is_hovered = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.click_location = (0, 0)
        self.starting_position = (self.center_x, self.center_y)

    def on_touch_down(self, touch):
        if super().on_touch_down(touch):
            return True
        if not self.collide_point(touch.x, touch.y):
            return False
        self.click_location = (touch.x, touch.y)
        self.starting_position = (self.center_x, self.center_y)
        touch.grab(self)
        self.is_grabbed = True
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
        if touch.grab_current is self or self.is_hovered:
            touch.ungrab(self)
            self.is_grabbed = False
            play_area = self.parent.parent.play_area
            if play_area.collide_point(self.center_x, self.center_y):
                self.center_x = play_area.center_x
                self.center_y = play_area.center_y
            else:
                self.center_x = self.starting_position[0]
                self.center_y = self.starting_position[1]
            return True
        return False

class Hand(BoxLayout):
    is_card_hovered = BooleanProperty(False)

    def on_touch_up(self, touch):
        if self.is_card_hovered:
            for card in self.children:
                if card.collide_point(touch.x, touch.y):
                    print("Card hovered and released")
                    if card.on_touch_up(touch):
                        print("Card released in hand")
                        if card.is_hovered:
                            print("Card released in hand and hovered")
                            if not card.collide_point(touch.x, touch.y):
                                print("Card released outside hand")
                                card.is_hovered = False
                                self.is_card_hovered = False
                                return True
        return False

    def on_motion(self, window, pos):
        for card in self.children:
            if card.collide_point(pos[0], pos[1]) and not card.is_hovered and not self.is_card_hovered:
                card.is_hovered = True
                self.is_card_hovered = True
                return True
            if not card.collide_point(pos[0], pos[1]) and card.is_hovered:
                card.is_hovered = False
                self.is_card_hovered = False
        return False

class CardGame(Widget):
    play_area = ObjectProperty(None)
    card1 = ObjectProperty(None)
    card2 = ObjectProperty(None)
    hand = ObjectProperty(None)

class CardGameApp(App):
    def build(self):
        game = CardGame()
        Window.bind(mouse_pos=game.hand.on_motion)
        game.hand.add_widget(Card())
        return game

if __name__ == '__main__':
    CardGameApp().run()
