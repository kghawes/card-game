from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.lang import Builder
from kivy.config import Config
from gui.combat_screen import CombatScreen
from gui.town_screen import TownScreen

Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
Config.set('graphics', 'resizable', '0')
Builder.load_file('gui/combat_screen.kv')
Builder.load_file('gui/town_screen.kv')
Builder.load_file('gui/card.kv')

class CardGame(Widget):
    """Main widget for the card game."""
    def start_quest(self):
        """Starts a quest in the game."""
        player = {
            'name': 'Test Player',
            'health': 10,
            'max_health': 10,
            'stamina': 3,
            'max_stamina': 3,
            'magicka': 3,
            'max_magicka': 3
        }
        enemy = {
            'name': 'Test Enemy',
            'health': 10,
            'max_health': 10,
            'stamina': 3,
            'max_stamina': 3,
            'magicka': 3,
            'max_magicka': 3
        }
        combat_screen = CombatScreen(player, enemy)
        self.add_widget(combat_screen)

class CardGameApp(App):
    """Main application class for the card game."""
    def __init__(self, event_manager, **kwargs):
        """Initializes the kivy app."""
        super().__init__(**kwargs)
        self.event_manager = event_manager

    def build(self):
        """Builds the card game application."""
        game = CardGame()
        town_screen = TownScreen(game)
        game.add_widget(town_screen)
        return game
