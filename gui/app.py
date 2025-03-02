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
    def __init__(self, event_manager, **kwargs):
        """Initializes the card game widget."""
        super().__init__(**kwargs)
        self.event_manager = event_manager

    def start_combat(self):
        """Starts a combat encounter in the game."""
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
        self.change_screen(CombatScreen(player, enemy))

    def change_screen(self, screen):
        """Changes the current screen of the game."""
        self.clear_widgets()
        self.add_widget(screen)
        self.event_manager.dispatch('set_screen', screen)

class CardGameApp(App):
    """Main application class for the card game."""
    def __init__(self, event_manager, **kwargs):
        """Initializes the kivy app."""
        super().__init__(self, event_manager, **kwargs)
        self.event_manager = event_manager

    def build(self):
        """Builds the card game application."""
        self.game = CardGame(self.event_manager)
        town_screen = TownScreen(self.game)
        self.game.add_widget(town_screen)
        return self.game
    
