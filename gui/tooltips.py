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
    
    def show(self, text):
        """
        Show the tooltip with the given text.
        """
        if not self.visible and text:
            self.tip_label.text = text
            self.visible = True
    
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
        self.x = pos[0] + 15
        self.y = pos[1] - 15 - self.height
