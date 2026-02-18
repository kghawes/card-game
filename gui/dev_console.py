"""
The module defines the debug console in the GUI.
"""

from kivy.uix.widget import Widget
from kivy.uix.textinput import TextInput
from kivy.properties import ObjectProperty

class DevConsoleInput(TextInput):
    """
    Text input for the dev console that handles command submission and history navigation.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        if keycode[1] == 'enter':
            self.parent.on_text_validate()
            return True
        elif keycode[1] == 'up':
            self.parent.previous_command()
            return True
        elif keycode[1] == 'down':
            self.parent.next_command()
            return True
        else:
            return super().keyboard_on_key_down(window, keycode, text, modifiers)
    
    def insert_text(self, substring, from_undo=False):
        substring = substring.replace("`", "")
        return super().insert_text(substring, from_undo)


class DevConsole(Widget):
    """
    Console for entering debug commands.
    """
    text_input = ObjectProperty(DevConsoleInput)
    text_output = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.history = [] # most recent first
        self.history_index = -1
        self.current_buffer = ""
        self.visible = False
    
    def show(self, screen):
        """Shows the console and restores unsubmitted text."""
        if not self.parent:
            screen.add_widget(self)
            self.text_input.focus = True
            if self.history_index == -1 and self.current_buffer:
                self.text_input.text = self.current_buffer
            self.visible = True
    
    def hide(self):
        """Hides the console and preserves unsubmitted text."""
        if self.parent:
            if self.history_index < 0 and self.text_input.text.strip():
                self.current_buffer = self.text_input.text
            self.parent.remove_widget(self)
            self.visible = False
    
    def previous_command(self):
        """
        Navigate to the previous command in history, if any.
        Stores unsubmitted text in current_buffer when first navigating up.
        """
        if self.history:
            if self.history_index == -1:
                self.current_buffer = self.text_input.text
            
            self.history_index += 1
            if self.history_index < len(self.history):
                self.text_input.text = self.history[self.history_index]
            else:
                self.history_index -= 1
        print(self.history_index)
    
    def next_command(self):
        """
        Navigate to the next command in history, if any.
        Restores unsubmitted text from current_buffer when reaching the end.
        """
        if self.history:
            if self.history_index > -1:
                self.history_index -= 1
                if self.history_index == -1:
                    self.text_input.text = self.current_buffer
                else:
                    self.text_input.text = self.history[self.history_index]
        print(self.history_index)
    
    def on_text_validate(self):
        """
        Submits the current command, adds it to history, and resets the input.
        """
        if self.parent:
            command = self.text_input.text.strip()
            event_manager = self.parent.event_manager
            if command:
                self.history.insert(0, command)
                self.history_index = -1
                self.current_buffer = ""
                self.text_input.text = ""
                event_manager.dispatch('debug_command_submitted', command)
            else:
                self.text_input.text = ""
        else:
            raise RuntimeError("Cannot submit command when dev console is not open!")
    
    def show_result(self, command, success, message):
        """
        Displays the result of a debug command execution.
        """
        if success:
            result_text = f"Successfully executed '{command}'\\n{message}"
        else:
            result_text = f"Failed to execute '{command}'\\n{message}"
        self.text_output.text += result_text + "\\n"
