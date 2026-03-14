"""Combat Screen Module for Card Game"""
from operator import indexOf
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.properties import ObjectProperty, BooleanProperty
from kivy.clock import Clock
import gui.gui_constants as constants
from gui.asset_cache import AssetCache
from gui.card import Card
from gui.tooltips import Tooltip
from gui.combat_log import CombatLog

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

    def add_to_hand(self, card: Card, index=0):
        """Adds a card to the hand and repositions the cards."""
        self.add_widget(card, index=index)
        self.position_cards()
    
    def remove_from_hand(self, card: Card):
        """Removes a card from the hand and repositions the cards."""
        self.remove_widget(card)
        self.position_cards()

    def draw(self, card_data: dict):
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
    
    def clear_hand(self):
        """Clears all cards from the hand."""
        for card in self.children[:]:
            self.remove_widget(card)
        self.position_cards()


class ScreenDarken(Widget):
    """Widget that darkens the screen and blocks input."""
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


class StatusIcon(Widget):
    """Widget representing a status icon."""
    status_texture = ObjectProperty(None)
    level = ObjectProperty(None)
    description = ObjectProperty(None)

    def __init__(self, status_id, level, **kwargs):
        """Initialize a new StatusIcon."""
        image_path = status_id.lower().replace(' ', '_')
        image_path = constants.STATUS_ICONS_PATH.format(image_path)
        self.status_texture = AssetCache.get_texture(image_path)
        self.level = str(level)
        super().__init__(**kwargs)


class CombatScreen(Widget):
    """Widget representing the combat screen of the card game."""
    STAT_LABELS = (
        ("health", "max_health", "Health"),
        ("stamina", "max_stamina", "Stamina"),
        ("magicka", "max_magicka", "Magicka"),
    )
    ATTRIBUTE_KEYS = (
        ("STRENGTH", "strength"),
        ("ENDURANCE", "endurance"),
        ("AGILITY", "agility"),
        ("SPEED", "speed"),
        ("INTELLIGENCE", "intelligence"),
        ("WILLPOWER", "willpower"),
        ("PERSONALITY", "personality"),
        ("LUCK", "luck"),
    )
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

    def __init__(
            self, player: dict, enemy: dict, event_manager, dev_console, **kwargs
            ):
        """Initializes the combat screen with the given properties."""
        super().__init__(**kwargs)
        self.event_manager = event_manager
        self.hand.screen = self
        self.player = player
        self.player_info.player_name_label.text = self.player['name']
        self.update_combatant_resources(self.player_info, self.player, "player")
        self.update_combatant_attributes(
            self.player_info, self.player.get('attributes', {}), "player"
        )
        self.enemy = enemy
        self.enemy_info.enemy_name_label.text = self.enemy['name']
        self.update_combatant_resources(self.enemy_info, self.enemy, "enemy")
        self.update_combatant_attributes(
            self.enemy_info, self.enemy.get('attributes', {}), "enemy"
        )
        self.wait_texture = AssetCache.get_texture('gui/assets/hourglass0.png')
        self.log_texture = AssetCache.get_texture('gui/assets/logbookclosed.png')
        self.tooltip = Tooltip()
        self.add_widget(self.tooltip)
        self.dev_console = dev_console
    
    def start_player_turn(self, statuses: dict):
        """Starts the player's turn."""
        self.end_turn_button.disabled = False
        Clock.unschedule(self.loop_textures)
        self.wait_texture = AssetCache.get_texture('gui/assets/hourglass0.png')
        self.update_player_statuses(statuses)

    def update_player_statuses(self, statuses: dict):
        """Updates the player's statuses on the screen."""
        for label in self.player_info.player_statuses.children:
            self.tooltip.remove_tooltip(label)
        self.player_info.player_statuses.clear_widgets()

        icon_size = 32
        x_spacing = 4
        y_spacing = 4
        label_offset = 33
        base_x = self.player_info.x
        base_y = self.player_info.y
        max_width = self.player_info.width
        x = base_x
        y = base_y

        for status_id, status_data in statuses.items():
            level = status_data['level']
            status_icon = StatusIcon(status_id, level)
            status_icon.size_hint = (None, None)

            label_width = 0
            for child in status_icon.children:
                if isinstance(child, Label):
                    child.texture_update()
                    label_width = child.texture_size[0]
                    break

            icon_width = max(icon_size, label_offset + label_width)
            if x != base_x and x + icon_width > base_x + max_width:
                x = base_x
                y += icon_size + y_spacing

            status_icon.size = (icon_width, icon_size)
            status_icon.pos = (x, y)
            self.player_info.player_statuses.add_widget(status_icon)

            description = status_data['description']
            self.tooltip.add_tooltip(status_icon, description)
            x += icon_width + x_spacing

    def update_enemy_statuses(self, statuses: dict):
        """Updates the enemy's statuses on the screen."""
        self.enemy_info.enemy_statuses.clear_widgets()
        y_offset = 0
        base_y = self.enemy_info.enemy_luck_label.y
        for status_id, level in statuses.items():
            status_label = Label(text=f"{status_id} ({level})")
            self.enemy_info.enemy_statuses.add_widget(status_label)
            status_label.size = (300, 33)
            status_label.size_hint = (None, None)
            x = 1192
            y_offset += 33
            y = base_y - y_offset
            status_label.pos = (x, y)

    def update_combatant_resources(self, info_widget, combatant, label_prefix):
        """Updates the resource stats of a combatant on the screen."""
        for stat_key, max_key, _ in self.STAT_LABELS:
            label_widget = getattr(info_widget, f"{label_prefix}_{stat_key}_label")
            label_widget.text = f"{combatant[stat_key]}/{combatant[max_key]}"

    def update_combatant_attributes(self, info_widget, attributes, label_prefix):
        """Updates the attributes of a combatant on the screen."""
        for attribute_key, label_suffix in self.ATTRIBUTE_KEYS:
            label_widget = getattr(info_widget, f"{label_prefix}_{label_suffix}_label")
            label_widget.text = str(attributes.get(attribute_key, 0))

    def update_stats(self, subject: str, stats_data: dict):
        """Updates the stats of the player or enemy."""
        target = self.player if subject == 'player' else self.enemy
        for key, value in stats_data.items():
            if key in target:
                target[key] = value
        if subject == 'player':
            self.update_combatant_resources(self.player_info, self.player, "player")
            self.update_combatant_attributes(
                self.player_info, self.player.get('attributes', {}), "player"
            )
            self.update_player_statuses(stats_data['statuses'])
        else:
            self.update_combatant_resources(self.enemy_info, self.enemy, "enemy")
            self.update_combatant_attributes(
                self.enemy_info, self.enemy.get('attributes', {}), "enemy"
            )
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

    def enemy_played_card(self, enemy_name: str, card_data: dict):
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
        if self.combat_log.log_toggled_on:
            self.combat_log.log_toggled_on = False
            self.log_texture = AssetCache.get_texture('gui/assets/logbookclosed.png')
            if not self.combat_log.timer_is_running:
                self.combat_log.hide_log()
        else:
            self.combat_log.log_toggled_on = True
            self.log_texture = AssetCache.get_texture('gui/assets/logbookopen.png')
            self.combat_log.show_log()

    def show_combat_results(self, player_wins, rewards):
        """Shows the combat results."""
        Clock.unschedule(self.loop_textures)
        self.combat_log.flush_queue(self.event_manager)
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

    def on_key_down(self, window, key, scancode, codepoint, modifier):
        """Handles key down events for the combat screen."""
        if key == 96:  # Tilde key
            if self.dev_console.visible:
                self.dev_console.hide()
            else:
                self.dev_console.show(self)
