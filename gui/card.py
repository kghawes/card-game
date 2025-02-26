from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.graphics import Rectangle, Color, RoundedRectangle
from kivy.vector import Vector
from kivy.properties import ObjectProperty, BooleanProperty, ColorProperty, StringProperty, NumericProperty
from kivy.clock import Clock
from kivy.core.window import Window
import gui_constants as constants
from asset_cache import AssetCache

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
    texture = ObjectProperty(None)
    formatted_type = StringProperty('None')

    def __init__(self, card_data, **kwargs):
        """Initializes a card with the given data."""
        super().__init__(**kwargs)
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
        self.texture = AssetCache.get_texture(f'assets/cards/{self.card_id}.png')
        self.cost = card_data['cost']
        self.effects = self.format_effects(card_data['effects'])
        self.formatted_type = f"{self.card_type} ({card_data['subtype']})" if 'subtype' in card_data else self.card_type
    
    def format_effects(self, effects):
        """Formats the effects of the card for display."""
        formatted_effects = []
        for effect, level in effects.items():
            formatted_effects.append(f"{effect} {level}")
        return '\n'.join(formatted_effects)

    def on_touch_down(self, touch):
        """When clicked, pick up the card."""
        if super().on_touch_down(touch):
            return True
        if not self.is_draggable or not self.collide_point(touch.x, touch.y):
            return False
        self.click_location = (touch.x, touch.y)
        self.starting_position = (self.center_x, self.center_y)
        touch.grab(self)
        self.hand_index = self.parent.children.index(self)
        animation_layer = self.parent.get_root_window().children[0].animation_layer
        hand = self.parent
        for card in hand.children:
            card.is_draggable = False
        hand.remove_from_hand(self)
        animation_layer.add_widget(self)
        return True

    def on_touch_move(self, touch):
        """Drag the card with the mouse."""
        if touch.grab_current is self:
            offset = tuple(Vector(*touch.pos) - Vector(*self.click_location))
            new_position = tuple(Vector(*self.starting_position) + Vector(*offset))
            self.center_x = max(self.width / 2, min(new_position[0], Window.width - self.width / 2))
            self.center_y = max(self.height / 2, min(new_position[1], Window.height - self.height / 2))
            return True
        return False

    def on_touch_up(self, touch):
        """Release a held card."""
        if touch.grab_current is self:
            touch.ungrab(self)
            play_area = self.get_root_window().children[0].play_area
            if play_area.collide_point(self.center_x, self.center_y):
                self.center_x = play_area.center_x
                self.center_y = play_area.center_y
                Clock.schedule_once(self.move_to_discard, 1)
            else:
                hand = self.get_root_window().children[0].hand
                self.parent.remove_widget(self)
                hand.add_to_hand(self, index=self.hand_index)
                for card in hand.children:
                    card.is_draggable = True
            return True
        return False

    def move_to_discard(self, dt):
        """Moves the card to the discard pile."""
        discard_pile = self.get_root_window().children[0].discard_pile
        self.center_x = discard_pile.center_x
        self.center_y = discard_pile.center_y
        self.parent.remove_widget(self)
        if discard_pile.children:
            discard_pile.remove_widget(discard_pile.children[0])
        discard_pile.add_widget(self)
        self.is_draggable = False
        hand = self.get_root_window().children[0].hand
        for card in hand.children:
            card.is_draggable = True