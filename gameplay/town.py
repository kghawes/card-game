"""
This module defines the Town class.
"""

import utils.constants as constants

class Town:
    """
    This class represents the 'overworld' visited between quests.
    """
    def enter_town(self, player, text_interface):
        """
        Go to town screen.
        """
        text_interface.send_message(constants.ENTER_TOWN_MESSAGE)
        selection = text_interface.town_options_prompt()
        if selection == 0:
            player.card_manager.library.open_library(text_interface)
