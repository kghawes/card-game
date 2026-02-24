"""
Module for the combat log widget in the card game GUI.
"""

from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.clock import Clock

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
        self.pending += event_manager.logger.get_combat_logs()
        if self.pending:
            Clock.schedule_interval(self.log_message, 0.33)
    
    def log_message(self, dt):
        if self.pending:
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