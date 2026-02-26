"""
Module for the combat log widget in the card game GUI.
"""

from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.clock import Clock

class CombatLog(Widget):
    """Widget representing the combat log."""
    combat_log_label = ObjectProperty(None)
    combat_log_scrollview = ObjectProperty(None)

    def __init__(self, **kwargs):
        """Initialize a new CombatLog."""
        super().__init__(**kwargs)
        self.queue = []
        # queue has the following structure:
        # [
        #     {
        #         "message": "Message text to display",
        #         "delay": 0.3,  # seconds to wait before showing the next message
        #         "sound": "sword_hit",
        #         "animation": "player_hit"
        #     },
        #     ...
        # ]
        self.timer_is_running = False
        self.log_toggled_on = False
        self.flush_in_progress = False
        self.message = ""
        self.remove_widget(self.combat_log_scrollview)  # temporary fix to hide the log until it's needed

    def get_log_messages(self, event_manager):
        """Fetches new log messages from the event manager."""
        new_messages = event_manager.logger.get_combat_logs()
        if new_messages:
            self.queue.extend(new_messages)
    
    def flush_queue(self, event_manager):
        """Flushes the message queue to the log display."""
        self.get_log_messages(event_manager)
        if self.queue and not self.flush_in_progress:
            self.show_log()
            self.flush_in_progress = True
            delay = 0.0
            while self.queue:
                # message_info = self.queue.pop(0)
                # self.message = message_info.get("message", "")
                # sound = message_info.get("sound", None)
                # animation = message_info.get("animation", None)
                self.message = self.queue.pop(0)
                Clock.schedule_once(self.display, delay)
                delay = 0.3 # message_info.get("delay", 0.3)
            self.flush_in_progress = False
            self.timer_is_running = True
            Clock.schedule_once(self.auto_hide_log, delay + 2)
    
    def display(self, dt):
        """Displays the current message."""
        if self.message:
            if self.combat_log_label.text:
                self.combat_log_label.text += "\n"
            self.combat_log_label.text += self.message
            self.message = ""
            self.combat_log_scrollview.scroll_y = 0
    
    def show_log(self):
        """Shows the combat log if it's not already visible."""
        if not self.combat_log_scrollview.parent:
            self.add_widget(self.combat_log_scrollview)
            self.log_shown = True

    def hide_log(self):
        """Hides the combat log."""
        if self.combat_log_scrollview.parent:
            self.remove_widget(self.combat_log_scrollview)
            self.log_shown = False
    
    def auto_hide_log(self, dt):
        """Automatically hides the combat log after a delay."""
        if not self.log_toggled_on:
            self.hide_log()
        self.timer_is_running = False

    # def flush_log_messages(self, event_manager):
    #     """Writes all pending log messages to the log display."""
    #     self.pending += event_manager.logger.get_combat_logs()
    #     if self.pending:
    #         Clock.schedule_interval(self.log_message, 0.33)
    
    # def log_message(self, dt):
    #     if self.pending:
    #         message = self.pending.pop(0)
    #         self.history.append(message)
    #         if self.combat_log_label.text:
    #             self.combat_log_label.text += "\n"
    #         self.combat_log_label.text += message
    #     if not self.pending:
    #         Clock.unschedule(self.log_message)
    #         if not self.log_shown:
    #             Clock.schedule_once(self.hide_message, 2)  
    
    # def hide_message(self, dt):
    #     """Hides the current message after a delay."""
    #     self.combat_log_label.text = ""

    # def show_history(self):
    #     """Displays the combat log history."""
    #     self.combat_log_label.text = "\n".join(self.history)
    #     self.log_shown = True
    
    # def hide_history(self):
    #     """Hides the combat log history."""
    #     self.combat_log_label.text = ""
    #     self.log_shown = False
