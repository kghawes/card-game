"""
This module defines the Tooltip class, which is used to display tooltips in the GUI.
"""
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ObjectProperty
from kivy.core.window import Window

class Tooltip(FloatLayout):
    """
    Tooltip class to display a tooltip in the GUI.
    """
    visible = ObjectProperty(False)
    tip_label = ObjectProperty(None)

    def __init__(self, **kwargs):
        """
        Initialize a new Tooltip.
        """
        super().__init__(**kwargs)
        Window.bind(on_motion=self.on_mouse_move)
        self.tooltips = {}
        self.enabled = True
    
    def _update_pos(self, pos):
        """
        Update the position of the tooltip.
        """
        if not self.tip_label.texture_size[1] or self.tip_label.width > 200:
            self.x = 99999
            self.y = 99999
        else:
            if pos[0] + self.width + 15 >= 1500:
                self.x = 1500 - self.width
            else:
                self.x = pos[0] + 15
            self.y = max(pos[1] - 15 - self.height, 0)

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
        if self.enabled and not self.visible and text:
            self.tip_label.text_size = (None, None)
            self.tip_label.size = (0, 0)
            self.tip_label.text = text
            self.visible = True
            self.height = self.tip_label.texture_size[1] + 8

            self.tip_label.texture_update()
            natural_width = self.tip_label.texture_size[0]
            final_width = min(natural_width, 200)
            self.tip_label.text_size = (final_width, None)
            self.tip_label.size = self.tip_label.texture_size
    
    def hide(self):
        """
        Hide the tooltip.
        """
        if self.visible or self.tip_label.text:
            self.visible = False
            self.tip_label.text = ""
    
    def on_mouse_move(self, window, event_type, event):
        """
        Handle mouse movement to update tooltip position.
        """
        pos = event.to_absolute_pos(event.sx, event.sy, window.width, window.height, 0)
        if self.enabled:
            if self.visible:
                self._update_pos(pos)
            for widget, text in self.tooltips.items():
                if widget.collide_point(*pos):
                    self.show(text)
                    self._update_pos(pos)
                    return
        self.hide()
    
    def disable(self):
        """
        Disable the tooltip.
        """
        self.enabled = False
        self.hide()
    
    def enable(self):
        """
        Enable the tooltip.
        """
        self.enabled = True
