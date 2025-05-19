"""Combat Screen Module for Card Game"""
from operator import indexOf
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.properties import ObjectProperty, BooleanProperty
from kivy.clock import Clock
import gui.gui_constants as constants
from gui.asset_cache import AssetCache
from gui.card import Card
from gui.tooltips import Tooltip

class Hand(FloatLayout):
    """Widget representing the player's hand of cards."""
    screen = ObjectProperty(None)

    def position_cards(self):
        """Positions the cards in the hand."""
        cards = self.children
        x = self.center_x
        y = self.center_y
        if len(cards) <= 5:
            for i, card in enumerate(cards):
                center_index = len(cards) // 2
                card.center_x = x + (i - center_index) * 208 + 104 * (1 - len(cards) % 2)
                card.center_y = y
        else:
            for i, card in enumerate(cards):
                card.center_x = i * (832 / (len(cards) - 1)) + 334
                card.center_y = y
    
    def add_to_hand(self, card, index=0):
        """Adds a card to the hand and repositions the cards."""
        self.add_widget(card, index=index)
        self.position_cards()
    
    def remove_from_hand(self, card):
        """Removes a card from the hand and repositions the cards."""
        self.remove_widget(card)
        self.position_cards()
    
    def draw(self, card_data):
        """Draws a card from the deck and adds it to the hand."""
        card = Card(card_data, self.screen)
        self.add_to_hand(card)
    
    def discard(self, index=None, card=None):
        """Discards a card from the hand."""
        if not card and index is not None and 0 <= index < len(self.children):
            card = self.children[index]
        elif not card:
            card = self.children[0]
        if card:
            card.move_to_discard()
            self.position_cards()


class CombatLog(Widget):
    """Widget representing the combat log."""
    combat_log_label = ObjectProperty(None)

    def __init__(self, **kwargs):
        """Initialize a new CombatLog."""
        super().__init__(**kwargs)
        self.history = []
        self.pending = []
        self.log_shown = False

    def flush_log_messages(self, event_manager):
        """Writes all pending log messages to the log display."""
        self.pending = event_manager.logger.get_combat_logs()
        if self.pending:
            Clock.schedule_interval(self.log_message, 0.33)
    
    def log_message(self, dt):
        message = self.pending.pop(0)
        self.history.append(message)
        if self.combat_log_label.text:
            self.combat_log_label.text += "\n"
        self.combat_log_label.text += message
        if not self.pending:
            Clock.unschedule(self.log_message)
            if not self.log_shown:
                Clock.schedule_once(self.hide_message, 2)  
    
    def hide_message(self, dt):
        """Hides the current message after a delay."""
        self.combat_log_label.text = ""

    def show_history(self):
        """Displays the combat log history."""
        self.combat_log_label.text = "\n".join(self.history)
        self.log_shown = True
    
    def hide_history(self):
        """Hides the combat log history."""
        self.combat_log_label.text = ""
        self.log_shown = False


class ScreenDarken(Widget):    
    def on_touch_down(self, touch):
        return True
    
    def on_touch_move(self, touch):
        return True
    
    def on_touch_up(self, touch):
        return True


class CombatResults(Widget):
    """Widget representing the combat results screen."""
    def __init__(self, event_manager, **kwargs):
        """Initializes the combat results widget."""
        super().__init__(**kwargs)
        self.event_manager = event_manager

    def back_to_quest(self):
        """Returns to the quest screen."""
        self.event_manager.dispatch('back_to_quest')


# class StatusIcon(Widget):
#     """Widget representing a status icon."""
#     status_texture = ObjectProperty(None)
#     status_name = ObjectProperty(None)
#     status_level = ObjectProperty(None)

#     def __init__(self, status_data, **kwargs):
#         """Initializes the status icon with the given data."""
#         super().__init__(**kwargs)
#         self.status_texture = AssetCache.get_texture(status_data['texture'])
#         self.status_name.text = status_data['name']
#         self.status_level.text = str(status_data['level'])
        # implement a method to load all the statuses on startup
        # implement status name and status data on game side
        # consider simpler implementation first


class CombatScreen(Widget):
    """Widget representing the combat screen of the card game."""
    play_area = ObjectProperty(None)
    hand = ObjectProperty(Hand)
    deck = ObjectProperty(None)
    discard_pile = ObjectProperty(None)
    animation_layer = ObjectProperty(None)
    show_deck = BooleanProperty(True)
    player = ObjectProperty(None)
    enemy = ObjectProperty(None)
    wait_texture = ObjectProperty(None)
    log_texture = ObjectProperty(None)
    combat_log = ObjectProperty(CombatLog)

    def __init__(self, player, enemy, event_manager, **kwargs):
        """Initializes the combat screen with the given properties."""
        super().__init__(**kwargs)
        self.event_manager = event_manager
        self.hand.screen = self
        self.player = player
        self.player_info.player_name_label.text = self.player['name']
        self.update_player_stats()
        self.enemy = enemy
        self.enemy_info.enemy_name_label.text = self.enemy['name']
        self.update_enemy_stats()
        self.wait_texture = AssetCache.get_texture('gui/assets/hourglass0.png')
        self.log_texture = AssetCache.get_texture('gui/assets/logbookclosed.png')
        self.tooltip = Tooltip()
        self.add_widget(self.tooltip)
    
    def start_player_turn(self, statuses):
        """Starts the player's turn."""
        self.end_turn_button.disabled = False
        Clock.unschedule(self.loop_textures)
        self.wait_texture = AssetCache.get_texture('gui/assets/hourglass0.png')
        self.update_player_statuses(statuses)

    def update_player_statuses(self, statuses):
        """Updates the player's statuses on the screen."""
        for label in self.player_info.player_statuses.children:
            self.tooltip.remove_tooltip(label)
        self.player_info.player_statuses.clear_widgets()
        y_offset = 0

        for status_id, status_data in statuses.items():
            name = status_data['name']
            level = status_data['level']
            status_label = Label(text=f"{name} ({level})")
            self.player_info.player_statuses.add_widget(status_label)
            status_label.size = (300, 33)
            status_label.size_hint = (None, None)
            x = 8
            y_offset += 33
            y = self.player_info.player_magicka_label.y - y_offset
            status_label.pos = (x, y)

            description = status_data['description']
            self.tooltip.add_tooltip(status_label, description)
    
    def update_enemy_statuses(self, statuses):
        """Updates the enemy's statuses on the screen."""
        self.enemy_info.enemy_statuses.clear_widgets()
        y_offset = 0
        for status_id, level in statuses.items():
            status_label = Label(text=f"{status_id} ({level})")
            self.enemy_info.enemy_statuses.add_widget(status_label)
            status_label.size = (300, 33)
            status_label.size_hint = (None, None)
            x = 1192
            y_offset += 33
            y = self.enemy_info.enemy_magicka_label.y - y_offset
            status_label.pos = (x, y)

    def update_player_stats(self):
        """Updates the player's stats on the screen."""
        self.player_info.player_health_label.text = f"Health: {self.player['health']}/{self.player['max_health']}"
        self.player_info.player_stamina_label.text = f"Stamina: {self.player['stamina']}/{self.player['max_stamina']}"
        self.player_info.player_magicka_label.text = f"Magicka: {self.player['magicka']}/{self.player['max_magicka']}"

    def update_enemy_stats(self):
        """Updates the enemy's stats on the screen."""
        self.enemy_info.enemy_health_label.text = f"Health: {self.enemy['health']}/{self.enemy['max_health']}"
        self.enemy_info.enemy_stamina_label.text = f"Stamina: {self.enemy['stamina']}/{self.enemy['max_stamina']}"
        self.enemy_info.enemy_magicka_label.text = f"Magicka: {self.enemy['magicka']}/{self.enemy['max_magicka']}"
    
    def update_stats(self, subject, stats_data):
        """Updates the stats of the player or enemy."""
        target = self.player if subject == 'player' else self.enemy
        for key, value in stats_data.items():
            if key in target:
                target[key] = value
        if subject == 'player':
            self.update_player_stats() 
            self.update_player_statuses(stats_data['statuses'])
        else:
            self.update_enemy_stats()
            self.update_enemy_statuses(stats_data['statuses'])

    def invalid_play(self):
        """Handles an invalid play."""
        card = self.animation_layer.children[0]
        card.return_to_hand()

    def end_turn(self):
        """Ends the current turn."""
        self.end_turn_button.disabled = True
        self.loop_textures(None)
        Clock.schedule_interval(self.loop_textures, 0.1)
        def discard_card(dt):
            if self.hand.children:
                self.hand.discard()
            else:
                Clock.unschedule(discard_card)
                self.event_manager.dispatch('end_turn')

        Clock.schedule_interval(discard_card, 0.1)
    
    def enemy_played_card(self, enemy_name, card_data):
        """Handles the enemy playing a card."""
        pass

    def loop_textures(self, dt):
        """Loops through the textures for the wait animation."""
        textures = [
            AssetCache.get_texture('gui/assets/hourglass0.png'),
            AssetCache.get_texture('gui/assets/hourglass45.png'),
            AssetCache.get_texture('gui/assets/hourglass90.png'),
            AssetCache.get_texture('gui/assets/hourglass135.png')
        ]
        self.wait_texture = textures[(indexOf(textures, self.wait_texture) + 1) % len(textures)]
    
    def empty_discard_pile(self):
        """Empties the discard pile."""
        for card in self.discard_pile.children:
            self.discard_pile.remove_widget(card)
    
    def toggle_log(self):
        """Toggles the log display."""
        if self.combat_log.log_shown:
            self.combat_log.hide_history()
            self.combat_log.log_shown = False
            self.log_texture = AssetCache.get_texture('gui/assets/logbookclosed.png')
        else:
            self.combat_log.show_history()
            self.combat_log.log_shown = True
            self.log_texture = AssetCache.get_texture('gui/assets/logbookopen.png')
    
    def show_combat_results(self, player_wins, rewards):
        """Shows the combat results."""
        Clock.unschedule(self.loop_textures)
        self.combat_log.flush_log_messages(self.event_manager)
        self.animation_layer.add_widget(ScreenDarken())
        combat_results = CombatResults(self.event_manager)
        self.add_widget(combat_results)
        if player_wins:
            combat_results.combat_results_label.text = "You win!"
            # TODO display rewards
        else:
            combat_results.combat_results_label.text = "You lose!"
            combat_results.continue_button.text = "Too bad"
            combat_results.continue_button.bind(on_release=lambda x: self.event_manager.dispatch('game_over'))
            # TODO implement game over logic and return to main menu instead of quitting
