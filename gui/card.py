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

    def __init__(self, card_data: dict, screen: Widget, **kwargs):
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

    def render_card(self, card_data: dict):
        """Renders the card with the given data."""
        card_type = card_data['type']
        type_colors = constants.CARD_TYPE_COLORS[card_type]
        self.card_type = card_type
        self.border_color = type_colors['border']
        self.resource_cost_color = constants.RESOURCE_COLORS[type_colors['resource']]
        self.cost_indicator = constants.RESOURCE_INDICATOR_OFFSETS[type_colors['indicator']]
        self.name = card_data['name']
        self.card_id = card_data['id']
        self.art_texture = AssetCache.get_texture(f'gui/assets/cards/{self.card_id}.png')
        self.art_bg_texture = AssetCache.get_texture(f'gui/assets/cards/{self.card_type}_bg.png')
        self.cost = str(card_data['cost'])
        effects = card_data['effects']
        self.effects = effects['card_text']
        subtypes = card_data.get('subtypes') or card_data.get('subtype')
        if subtypes:
            if isinstance(subtypes, (list, tuple, set)):
                subtype_text = ", ".join(subtypes).replace("_", " ")
            else:
                subtype_text = subtypes
            self.formatted_type = f"{self.card_type} ({subtype_text})"
        else:
            self.formatted_type = self.card_type
        self.tooltip_text = effects['tooltip_text']
        self.screen.tooltip.add_tooltip(self, self.tooltip_text)

    def on_touch_down(self, touch) -> bool:
        """When clicked, pick up the card. Return true to stop event propagation."""
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
        """Release a held card. Return true to stop event propagation."""
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
        """Return the card to the hand."""
        self.parent.remove_widget(self)
        self.hand.add_to_hand(self, index=self.hand_index)
        for card in self.hand.children:
            card.is_draggable = True
    
    def show_card_effect(self):
        """Show the card play effects, then move to discard."""
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
        self.screen.tooltip.remove_tooltip(self)
