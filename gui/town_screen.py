from kivy.uix.widget import Widget
from kivy.uix.button import Button

class TownScreen(Widget):
    """Widget representing the town screen of the card game."""
    def __init__(self, game, **kwargs):
        super().__init__(**kwargs)
        self.game = game
    
    def start_quest(self):
        self.parent.remove_widget(self)
        self.game.start_quest()