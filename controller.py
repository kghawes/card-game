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
        self.game.start_game()
    
    def send_logs(self):
        """Send logs to the GUI."""
        self.app.game.screen.combat_log.flush_log_messages(self.event_manager)
    
    # Game events

    def subscribe_to_game_events(self):
        """Subscribe to game events."""
        self.event_manager.subscribe('start_game', self.handle_start_game)
        self.event_manager.subscribe('start_quest', self.handle_start_quest)
        self.event_manager.subscribe('start_combat', self.handle_start_combat)
        self.event_manager.subscribe('start_action_phase', self.handle_start_action_phase)
        self.event_manager.subscribe('card_not_playable', self.handle_card_not_playable)
        self.event_manager.subscribe('card_resolved', self.handle_card_resolved)
        self.event_manager.subscribe('end_enemy_turn', self.handle_end_enemy_turn)
        self.event_manager.subscribe('end_combat', self.handle_end_combat)

    def handle_start_game(self):
        """Handle starting the game."""
        self.event_manager.logger.log("Game event fired: start_game", True)
        self.app.run()

    def handle_start_quest(self, quest):
        """Handle starting a quest."""
        self.event_manager.logger.log("Game event fired: start_quest", True)
        self.app.game.start_quest(quest)

    def handle_start_combat(self, enemy):
        """Handle starting combat."""
        self.event_manager.logger.log("Game event fired: start_combat", True)
        self.app.game.start_combat(self.game.player.get_combatant_data(), enemy.get_combatant_data())
    
    def handle_start_action_phase(self, hand):
        """Handle starting the action phase."""
        self.event_manager.logger.log("Game event fired: start_action_phase", True)
        self.app.game.screen.update_stats('player', self.game.player.get_combatant_data())
        for card in reversed(hand[:]):
            self.app.game.screen.hand.draw(card.get_card_data())

    def handle_card_not_playable(self):
        """Handle a card that cannot be played."""
        self.event_manager.logger.log("Game event fired: card_not_playable", True)
        self.send_logs()
        self.app.game.screen.invalid_play()

    def handle_card_resolved(self):
        """Handle a card that has been resolved."""
        self.event_manager.logger.log("Game event fired: card_resolved", True)
        self.send_logs()
        self.app.game.screen.update_stats('player', self.game.player.get_combatant_data())
        self.app.game.screen.update_stats('enemy', self.game.enemy.get_combatant_data())
        self.app.game.screen.animation_layer.children[-1].show_card_effect() # Ensure we are using the card and not something else in the animation layer

    def handle_end_enemy_turn(self):
        """Handle end of enemy turn."""
        self.event_manager.logger.log("Game event fired: end_enemy_turn", True)
        self.send_logs()
        self.app.game.screen.update_stats('player', self.game.player.get_combatant_data())
        self.app.game.screen.update_stats('enemy', self.game.enemy.get_combatant_data())
        self.event_manager.dispatch('start_player_turn')
    
    def handle_end_combat(self):
        """Handle end of combat."""
        self.event_manager.logger.log("Game event fired: end_combat", True)
        if self.game.player.is_alive():
            self.game.player.combat_cleanup()
            rewards = self.game.enemy.get_rewards(
                self.game.player.character_class,
                self.game.card_cache
                )
            # TODO give rewards to player
            self.app.game.screen.show_combat_results(True, rewards)
            # TODO make rewards optional
        else:
            self.app.game.screen.show_combat_results(False, None)

    # GUI events

    def subscribe_to_gui_events(self):
        """Subscribe to GUI events."""
        self.app.event_manager.subscribe('initiate_quest', self.handle_initiate_quest)
        self.app.event_manager.subscribe('initiate_encounter', self.handle_initiate_encounter)
        self.app.event_manager.subscribe('start_player_turn', self.handle_start_player_turn)
        self.app.event_manager.subscribe('play_card', self.handle_play_card)
        self.app.event_manager.subscribe('end_turn', self.handle_end_turn)
        self.app.event_manager.subscribe('back_to_quest', self.handle_back_to_quest)
        self.app.event_manager.subscribe('game_over', self.handle_game_over) 

    def handle_initiate_quest(self):
        """Handle initiating a quest."""
        self.event_manager.logger.log("GUI event fired: initiate_quest", True)
        self.game.start_quest()

    def handle_initiate_encounter(self):
        """Handle initiating an encounter."""
        self.event_manager.logger.log("GUI event fired: initiate_encounter", True)
        self.game.start_encounter()
    
    def handle_start_player_turn(self):
        """Handle starting player turn."""
        self.event_manager.logger.log("GUI event fired: start_player_turn", True)
        self.game.combat_manager.beginning_of_turn(self.game.player, self.game.enemy, self.game.registries)
        statuses = self.game.player.get_combatant_data()['statuses']
        self.app.game.screen.start_player_turn(statuses)

    def handle_play_card(self, index_in_hand):
        """Handle playing a card."""
        self.event_manager.logger.log("GUI event fired: play_card", True)
        card = self.game.player.card_manager.hand[index_in_hand]
        self.game.combat_manager.play_card(self.game.player, self.game.enemy, card, self.game.registries)

    def handle_end_turn(self):
        """Handle ending the turn."""
        self.event_manager.logger.log("GUI event fired: end_turn", True)
        self.game.combat_manager.end_of_turn(self.game.player, self.game.registries.statuses)
        self.game.combat_manager.do_enemy_turn(self.game.player, self.game.enemy, self.game.registries)

    def handle_back_to_quest(self):
        """Handle going back to the quest screen."""
        self.event_manager.logger.log("GUI event fired: back_to_quest", True)
        self.app.game.start_quest(self.game.quest)
    
    def handle_game_over(self):
        """Handle game over."""
        self.event_manager.logger.log("GUI event fired: game_over", True)
        self.app.stop()
