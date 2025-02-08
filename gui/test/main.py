from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import (
    NumericProperty, ReferenceListProperty, ObjectProperty, BooleanProperty
)
from kivy.clock import Clock
from kivy.config import Config
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')


class PlayArea(Widget):
    def on_touch_up(self, touch):
        if super().on_touch_up(touch):
            return True
        if not self.collide_point(touch.x, touch.y):
            return False
        
        for child in self.walk():
            if isinstance(child, Card) and child.is_grabbed:
                # Do something when a card is grabbed and touch is within PlayArea
                print("Card is grabbed and touch is within PlayArea")
                return True
        
        return True


class Card(Widget):
    is_grabbed = BooleanProperty(False)  # Add this line

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
        self.is_grabbed = True  # Update grabbed state
        return True

    def on_touch_move(self, touch):
        offset_x = touch.x - self.click_location[0]
        offset_y = touch.y - self.click_location[1]
        if touch.grab_current is self:
            self.center_x = self.starting_position[0] + offset_x
            self.center_y = self.starting_position[1] + offset_y
            return True
        return False
    
    def on_touch_up(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self)
            self.is_grabbed = False  # Update grabbed state
            return True
        return False


class CardGame(Widget):
    card = ObjectProperty(None)
    play_area = ObjectProperty(None)
    


class CardGameApp(App):
    def build(self):
        game = CardGame()
        #Clock.schedule_interval(game.update, 1.0 / 60.0)
        return game


if __name__ == '__main__':
    CardGameApp().run()