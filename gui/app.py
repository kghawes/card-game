from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.lang import Builder
from kivy.config import Config
from combat_screen import CombatScreen
from town_screen import TownScreen

Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
Config.set('graphics', 'resizable', '0')
Builder.load_file('combat_screen.kv')
Builder.load_file('town_screen.kv')
Builder.load_file('card.kv')

class CardGame(Widget):
    """Main widget for the card game."""
    def start_quest(self):
        """Starts a quest in the game."""
        combat_screen = CombatScreen()
        self.add_widget(combat_screen)

class CardGameApp(App):
    """Main application class for the card game."""
    
    def build(self):
        """Builds the card game application."""
        game = CardGame()
        town_screen = TownScreen(game)
        game.add_widget(town_screen)
        return game

CardGameApp().run()