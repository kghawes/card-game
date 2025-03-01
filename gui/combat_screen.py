"""Combat Screen Module for Card Game"""
from operator import indexOf
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ObjectProperty, BooleanProperty
from kivy.clock import Clock
import gui.gui_constants as constants
from gui.asset_cache import AssetCache
from gui.card import Card

class Hand(FloatLayout):
    """Widget representing the player's hand of cards."""

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

    def __init__(self, player, enemy, **kwargs):
        """Initializes the combat screen with the given properties."""
        super().__init__(**kwargs)
        self.player = player
        self.player_info.player_name_label.text = self.player['name']
        self.update_player_stats()
        self.enemy = enemy
        self.enemy_info.enemy_name_label.text = self.enemy['name']
        self.update_enemy_stats()

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

    def load(self):
        test_card = Card({
            'type': 'WEAPON',
            'subtype': 'Long Blade',
            'name': 'Iron Longsword',
            'id': 1,
            'cost': '3',
            'effects': {
                'Physical Damage Target': 2
                }
            }, self.animation_layer, self.hand, self.play_area, self.discard_pile)
        self.hand.add_widget(test_card)
        self.hand.position_cards()
        self.wait_texture = AssetCache.get_texture('gui/assets/hourglass0.png')

    def end_turn(self):
        """Ends the current turn."""
        self.load()
        self.end_turn_button.disabled = True
        Clock.schedule_interval(self.loop_textures, 0.25)

    def loop_textures(self, dt):
        """Loops through the textures for the wait animation."""
        textures = [
            AssetCache.get_texture('gui/assets/hourglass0.png'),
            AssetCache.get_texture('gui/assets/hourglass45.png'),
            AssetCache.get_texture('gui/assets/hourglass90.png'),
            AssetCache.get_texture('gui/assets/hourglass135.png')
        ]
        self.wait_texture = textures[(indexOf(textures, self.wait_texture) + 1) % len(textures)]
