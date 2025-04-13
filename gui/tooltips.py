from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ObjectProperty
from kivy.core.window import Window

class Tooltip(FloatLayout):
    """Tooltip class to display a tooltip in the GUI."""
    visible = ObjectProperty(False)
    tip_label = ObjectProperty(None)

    def __init__(self, **kwargs):
        """
        Initialize a new Tooltip.
        """
        super().__init__(**kwargs)
        Window.bind(on_motion=self.on_mouse_move)
        self.tooltips = {}
    
    def _update_pos(self, pos):
        """
        Update the position of the tooltip.
        """
        self.x = pos[0] + 15
        self.y = pos[1] - 15 - self.height

    def add_tooltip(self, widget, text):
        """
        Add a tooltip to a widget.
        """
        self.tooltips[widget] = text

    def remove_tooltip(self, widget):
        """
        Remove a tooltip from a widget.
        """
        if widget in self.tooltips:
            del self.tooltips[widget]
    
    def show(self, text):
        """
        Show the tooltip with the given text.
        """
        if not self.visible and text:
            self.tip_label.text = text
            self.visible = True
            self.height = self.tip_label.texture_size[1] + 8
    
    def hide(self):
        """
        Hide the tooltip.
        """
        if self.visible or self.tip_label.text:
            self.visible = False
            self.tip_label.text = " "
    
    def on_mouse_move(self, window, event_type, event):
        """
        Handle mouse movement to update tooltip position.
        """
        pos = event.to_absolute_pos(event.sx, event.sy, window.width, window.height, 0)
        if self.visible:
            self._update_pos(pos)
        for widget, text in self.tooltips.items():
            if widget.collide_point(*pos):
                self.show(text)
                self._update_pos(pos)
                return
        self.hide()
