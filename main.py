from core.game import Game
#from gui.app import CardGameApp
#from controller import Controller
#from utils.event_manager import EventManager
import os

with open(os.path.join(os.path.expanduser("~"), "game_log.txt"), "w") as file:
    file.write(f"Working Directory: {os.getcwd()}\n")


#event_manager = EventManager()
game = Game(None)#event_manager)
#app = CardGameApp(event_manager)
##controller = Controller(game, app, event_manager)
#controller.start_game()