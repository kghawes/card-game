"""Game controller module."""

class Controller:
    """Game controller to manage game state and GUI."""
    def __init__(self, game, app, event_manager):
        """Initialize the game controller."""
        self.game = game
        self.app = app
        self.event_manager = event_manager
        self.subscribe_to_game_events()
        self.subscribe_to_gui_events()
    
    def start_game(self):
        """Start the game."""
        self.app.run()
    
    def subscribe_to_game_events(self):
        """Subscribe to game events."""
        self.event_manager.subscribe('start_combat', self.handle_start_combat)
        self.event_manager.subscribe('end_combat', self.handle_end_combat)
        self.event_manager.subscribe('draw_card', self.handle_draw_card)
        self.event_manager.subscribe('discard_cards', self.handle_discard_cards)
        self.event_manager.subscribe('empty_discard_pile', self.handle_empty_discard_pile)
    
    def handle_start_combat(self, player, enemy):
        """Handle starting combat."""
        self.app.game.start_combat(player, enemy)

    def handle_end_combat(self):
        """Handle ending combat."""
        pass
    
    def handle_draw_card(self, card):
        """Handle drawing a card."""
        self.current_screen.hand.draw(card.get_card_data())

    def handle_empty_discard_pile(self):
        """Handle emptying the discard pile."""
        self.current_screen.empty_discard_pile()

    def handle_discard_card(self, index_in_hand):
        """Handle discarding cards."""
        self.current_screen.hand.discard(index_in_hand)
    
    def subscribe_to_gui_events(self):
        """Subscribe to GUI events."""
        self.app.event_manager.subscribe('set_screen', self.handle_set_screen)
        self.app.event_manager.subscribe('play_card', self.handle_play_card)
        self.app.event_manager.subscribe('end_turn', self.handle_end_turn)

    def handle_set_screen(self, screen):
        """Handle setting the screen."""
        self.current_screen = screen

    def handle_play_card(self, index_in_hand):
        """Handle playing a card."""
        pass

    def handle_end_turn(self):
        """Handle ending the turn."""
        pass

