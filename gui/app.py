"""
Main application module for the card game GUI.
"""

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.lang import Builder
from kivy.config import Config
from gui.combat_screen import CombatScreen
from gui.town_screen import TownScreen
from gui.quest_screen import QuestScreen

Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
Config.set('graphics', 'resizable', '0')
Builder.load_file('gui/combat_screen.kv')
Builder.load_file('gui/town_screen.kv')
Builder.load_file('gui/quest_screen.kv')
Builder.load_file('gui/card.kv')
Builder.load_file('gui/tooltips.kv')

class CardGame(Widget):
    """Main widget for the card game."""
    def __init__(self, event_manager, **kwargs):
        """Initializes the card game widget."""
        super().__init__(**kwargs)
        self.event_manager = event_manager

    def start_quest(self, quest):
        """Starts a quest in the game."""
        self.change_screen(QuestScreen(quest, self.event_manager))
        # TODO - pass quest data to QuestScreen in the form of a dictionary or some other data structure

    def start_combat(self, player_data, enemy_data):
        """Starts a combat encounter in the game."""
        self.change_screen(CombatScreen(player_data, enemy_data, self.event_manager))
        self.event_manager.dispatch('start_player_turn')

    def change_screen(self, screen):
        """Changes the current screen of the game."""
        self.clear_widgets()
        self.add_widget(screen)
        self.screen = screen

class CardGameApp(App):
    """Main application class for the card game."""
    def __init__(self, event_manager, **kwargs):
        """Initializes the kivy app."""
        super().__init__(**kwargs)
        self.event_manager = event_manager

    def build(self):
        """Builds the card game application."""
        self.game = CardGame(self.event_manager)
        Window.bind(on_key_down=self.on_key_down)
        town_screen = TownScreen(self.game)
        self.game.add_widget(town_screen)
        return self.game
    
    def on_key_down(self, window, key, scancode, codepoint, modifier):
        """Handles key down events for the application."""
        if isinstance(self.game.screen, CombatScreen):
            self.game.screen.on_key_down(window, key, scancode, codepoint, modifier)
