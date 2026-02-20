"""
Main entry point for the card game application.
"""
from utils.event_manager import EventManager
from core.game import Game
from gui.app import CardGameApp
from controller import Controller

event_manager = EventManager()
game = Game(event_manager)
app = CardGameApp(event_manager)
controller = Controller(game, app, event_manager)
controller.start_game()
