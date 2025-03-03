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
    
    # Game events

    def subscribe_to_game_events(self):
        """Subscribe to game events."""
        self.event_manager.subscribe('start_combat', self.handle_start_combat)
        self.event_manager.subscribe('player_defeat', self.handle_player_defeat)
        self.event_manager.subscribe('start_player_turn', self.handle_start_player_turn)
        self.event_manager.subscribe('card_not_playable', self.handle_card_not_playable)
        self.event_manager.subscribe('player_victory', self.handle_player_victory)
        self.event_manager.subscribe('update_statuses', self.handle_update_statuses)
        self.event_manager.subscribe('draw_card', self.handle_draw_card)
        self.event_manager.subscribe('discard_card', self.handle_discard_card)
        self.event_manager.subscribe('empty_discard_pile', self.handle_empty_discard_pile)
        self.event_manager.subscribe('stats_changed', self.handle_stats_changed)
    
    def handle_start_combat(self, enemy):
        """Handle starting combat."""
        self.app.game.start_combat(self.game.player.get_player_data(), enemy)

    def handle_player_defeat(self):
        """Handle player defeat."""
        self.app.game.player_defeat()
    
    def handle_start_player_turn(self):
        """Handle starting player turn."""
        statuses = self.game.player.status_manager.get_statuses()
        hand = [card.get_card_data() for card in self.game.player.card_manager.hand]
        self.current_screen.start_player_turn(statuses, hand)

    def handle_card_not_playable(self):
        """Handle a card that cannot be played."""
        self.current_screen.card_not_playable()

    def handle_player_victory(self, rewards, player_leveled_up):
        """Handle player victory."""
        self.app.game.player_victory(rewards, player_leveled_up)
    
    def handle_update_statuses(self, combatant):
        """Handle updating statuses."""
        if not combatant.is_enemy:
            statuses = self.game.player.status_manager.get_statuses()
            self.current_screen.update_statuses('player', statuses)
        else:
            statuses = self.game.enemy.status_manager.get_statuses()
            self.current_screen.update_statuses('enemy', statuses)

    def handle_draw_card(self, card):
        """Handle drawing a card."""
        self.current_screen.hand.draw(card.get_card_data())

    def handle_empty_discard_pile(self):
        """Handle emptying the discard pile."""
        self.current_screen.empty_discard_pile()

    def handle_discard_card(self, index_in_hand):
        """Handle discarding cards."""
        self.current_screen.hand.discard(index_in_hand)
    
    def handle_stats_changed(self, combatant):
        """Handle stats changes."""
        stats_data = {
            'health': combatant.get_health(),
            'max_health': combatant.get_max_health(),
            'stamina': combatant.get_stamina(),
            'max_stamina': combatant.get_max_stamina(),
            'magicka': combatant.get_magicka(),
            'max_magicka': combatant.get_max_magicka()
        }
        subject = 'player' if not combatant.is_enemy else 'enemy'
        self.current_screen.update_stats(subject, stats_data)

    # GUI events

    def subscribe_to_gui_events(self):
        """Subscribe to GUI events."""
        self.app.event_manager.subscribe('initiate_encounter', self.handle_initiate_encounter)
        self.app.event_manager.subscribe('set_screen', self.handle_set_screen)
        self.app.event_manager.subscribe('play_card', self.handle_play_card)
        self.app.event_manager.subscribe('end_turn', self.handle_end_turn)
    
    def handle_initiate_encounter(self, encounter):
        """Handle initiating an encounter."""
        self.game.start_encounter(encounter)

    def handle_set_screen(self, screen):
        """Handle setting the screen."""
        self.current_screen = screen

    def handle_play_card(self, index_in_hand):
        """Handle playing a card."""
        pass

    def handle_end_turn(self):
        """Handle ending the turn."""
        pass

