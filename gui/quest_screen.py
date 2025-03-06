from kivy.uix.widget import Widget

class QuestScreen(Widget):
    """Widget representing the quest screen of the card game."""
    def __init__(self, quest, event_manager, **kwargs):
        super().__init__(**kwargs)
        self.quest = quest
        self.event_manager = event_manager
    
    def start_encounter(self):
        self.event_manager.dispatch('initiate_encounter')