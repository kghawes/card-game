from kivy.uix.widget import Widget

class TownScreen(Widget):
    """Widget representing the town screen of the card game."""
    def __init__(self, game, **kwargs):
        super().__init__(**kwargs)
        self.game = game
    
    def start_quest(self):
        self.parent.remove_widget(self)
        self.game.event_manager.dispatch('initiate_quest')