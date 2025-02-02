"""
This module defines the Town class.
"""
import utils.constants as constants

class Town:
    """
    This class represents the 'overworld' visited between quests.
    """
    def enter_town(self, player, text_interface, effect_registry):
        """
        Go to town screen.
        """
        while True:
            text_interface.send_message(constants.ENTER_TOWN_MESSAGE)
            selection = text_interface.town_options_prompt()
            if selection == 0:  # Library
                player.card_manager.library.open_library(
                    player.card_manager, text_interface, effect_registry
                    )
            elif selection == 1:  # Merchant
                pass
            elif selection == 2:  # Quest
                return
            else:
                assert False
