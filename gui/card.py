from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.graphics import Rectangle, Color, RoundedRectangle
from kivy.vector import Vector
from kivy.properties import ObjectProperty, BooleanProperty, ColorProperty, StringProperty, NumericProperty
from kivy.clock import Clock
from kivy.core.window import Window
import gui.gui_constants as constants
from gui.asset_cache import AssetCache

class Card(Widget):
    """Widget representing a card."""
    is_draggable = BooleanProperty(True)
    border_color = ColorProperty([0, 0, 0, 0])
    resource_cost_color = ColorProperty([0, 0, 0, 0])
    cost_indicator = ObjectProperty([0, 0, 0, 0, 0, 0])
    card_type = StringProperty('NONE')
    name = StringProperty('Card Name')
    cost = StringProperty('0')
    effects = StringProperty('No Effect')
    art_texture = ObjectProperty(None)
    art_bg_texture = ObjectProperty(None)
    formatted_type = StringProperty('None')

    def __init__(self, card_data, screen, **kwargs):
        """Initializes a card with the given data."""
        super().__init__(**kwargs)
        self.screen = screen
        self.animation_layer = screen.animation_layer
        self.hand = screen.hand
        self.play_area = screen.play_area
        self.discard_pile = screen.discard_pile
        self.click_location = (0, 0)
        self.starting_position = (self.center_x, self.center_y)
        self.hand_index = 0
        self.render_card(card_data)

    def render_card(self, card_data):
        """Renders the card with the given data."""
        self.card_type = card_data['type']
        self.border_color = constants.CARD_TYPE_COLORS[self.card_type]['border']
        self.resource_cost_color = constants.RESOURCE_COLORS[constants.CARD_TYPE_COLORS[self.card_type]['resource']]
        self.cost_indicator = constants.RESOURCE_INDICATOR_OFFSETS[constants.CARD_TYPE_COLORS[self.card_type]['indicator']]
        self.name = card_data['name']
        self.card_id = card_data['id']
        self.art_texture = AssetCache.get_texture(f'gui/assets/cards/{self.card_id}.png')
        self.art_bg_texture = AssetCache.get_texture(f'gui/assets/cards/{self.card_type}_bg.png')
        self.cost = str(card_data['cost'])
        self.effects = self.format_effects(card_data['effects'])
        self.formatted_type = f"{self.card_type} ({card_data['subtype']})" if 'subtype' in card_data else self.card_type
    
    def format_effects(self, effects) -> str:
        """Formats the effects of the card for display."""
        formatted_effects = []
        for effect, level in effects.items():
            formatted_effects.append(f"{effect} {level}")
        return '\n'.join(formatted_effects)

    def on_touch_down(self, touch) -> bool:
        """When clicked, pick up the card."""
        if not self.is_draggable or not self.collide_point(touch.x, touch.y):
            return False
        self.click_location = (touch.x, touch.y)
        self.starting_position = (self.center_x, self.center_y)
        touch.grab(self)
        self.hand_index = self.parent.children.index(self)
        hand = self.parent
        for card in hand.children:
            card.is_draggable = False
        hand.remove_from_hand(self)
        self.animation_layer.add_widget(self)
        self.screen.tooltip.disable()
        return True

    def on_touch_move(self, touch) -> bool:
        """Drag the card with the mouse."""
        if touch.grab_current is self:
            offset = tuple(Vector(*touch.pos) - Vector(*self.click_location))
            new_position = tuple(Vector(*self.starting_position) + Vector(*offset))
            self.center_x = max(self.width / 2, min(new_position[0], Window.width - self.width / 2))
            self.center_y = max(self.height / 2, min(new_position[1], Window.height - self.height / 2))
            return True
        return False

    def on_touch_up(self, touch) -> bool:
        """Release a held card."""
        if touch.grab_current is self:
            self.screen.tooltip.enable()
            touch.ungrab(self)
            if self.play_area.collide_point(self.center_x, self.center_y):
                self.center_x = self.play_area.center_x
                self.center_y = self.play_area.center_y
                self.screen.event_manager.dispatch('play_card', self.hand_index)
            else:
                self.return_to_hand()
            return True
        return False

    def return_to_hand(self):
        self.parent.remove_widget(self)
        self.hand.add_to_hand(self, index=self.hand_index)
        for card in self.hand.children:
            card.is_draggable = True
    
    def show_card_effect(self):
        """Show the card play effects."""
        Clock.schedule_once(self.move_to_discard, 1)

    def move_to_discard(self, dt=0):
        """Moves the card to the discard pile."""
        self.center_x = self.discard_pile.center_x
        self.center_y = self.discard_pile.center_y
        self.parent.remove_widget(self)
        self.screen.empty_discard_pile()
        self.discard_pile.add_widget(self)
        self.is_draggable = False
        for card in self.hand.children:
            card.is_draggable = True