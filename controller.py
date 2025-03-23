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
        print("Game event fired: start_game")
        self.app.run()

    def handle_start_quest(self, quest):
        """Handle starting a quest."""
        print("Game event fired: start_quest")
        self.app.game.start_quest(quest)

    def handle_start_combat(self, enemy):
        """Handle starting combat."""
        print("Game event fired: start_combat")
        self.app.game.start_combat(self.game.player.get_combatant_data(), enemy.get_combatant_data())
    
    def handle_start_action_phase(self, hand):
        """Handle starting the action phase."""
        print("Game event fired: start_action_phase")
        self.app.game.screen.update_stats('player', self.game.player.get_combatant_data())
        for card in reversed(hand[:]):
            self.app.game.screen.hand.draw(card.get_card_data())

    def handle_card_not_playable(self):
        """Handle a card that cannot be played."""
        print("Game event fired: card_not_playable")
        self.app.game.screen.invalid_play()

    def handle_card_resolved(self):
        """Handle a card that has been resolved."""
        print("Game event fired: card_resolved")
        self.app.game.screen.update_stats('player', self.game.player.get_combatant_data())
        self.app.game.screen.update_stats('enemy', self.game.enemy.get_combatant_data())
        self.app.game.screen.animation_layer.children[-1].show_card_effect() # Ensure we are using the card and not something else in the animation layer

    def handle_end_enemy_turn(self):
        """Handle end of enemy turn."""
        print("Game event fired: end_enemy_turn")
        self.app.game.screen.update_stats('player', self.game.player.get_combatant_data())
        self.app.game.screen.update_stats('enemy', self.game.enemy.get_combatant_data())
        self.event_manager.dispatch('start_player_turn')
    
    def handle_end_combat(self):
        """Handle end of combat."""
        print("Game event fired: end_combat")
        if self.game.player.is_alive():
            self.game.player.combat_cleanup(self.game.registries.statuses)
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

    def handle_initiate_quest(self):
        """Handle initiating a quest."""
        print("GUI event fired: initiate_quest")
        self.game.start_quest()

    def handle_initiate_encounter(self):
        """Handle initiating an encounter."""
        print("GUI event fired: initiate_encounter")
        self.game.start_encounter()
    
    def handle_start_player_turn(self):
        """Handle starting player turn."""
        print("GUI event fired: start_player_turn")
        self.game.combat_manager.beginning_of_turn(self.game.player, self.game.enemy, self.game.registries)
        statuses = self.game.player.get_combatant_data()['statuses']
        hand = [card.get_card_data() for card in self.game.player.card_manager.hand]
        self.app.game.screen.start_player_turn(statuses, hand)

    def handle_play_card(self, index_in_hand):
        """Handle playing a card."""
        print("GUI event fired: play_card")
        card = self.game.player.card_manager.hand[index_in_hand]
        self.game.combat_manager.play_card(self.game.player, self.game.enemy, card, self.game.registries)

    def handle_end_turn(self):
        """Handle ending the turn."""
        print("GUI event fired: end_turn")
        self.game.combat_manager.end_of_turn(self.game.player, self.game.registries.statuses)
        self.game.combat_manager.do_enemy_turn(self.game.player, self.game.enemy, self.game.registries)

    def handle_back_to_quest(self):
        """Handle going back to the quest screen."""
        print("GUI event fired: back_to_quest")
        self.app.game.start_quest(self.game.quest)
