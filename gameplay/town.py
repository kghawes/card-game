"""This module defines the Town class."""

import utils.constants as constants

class Town:
    """This class represents the 'overworld' town."""
    def enter_town(self, text_interface):
        """Go to town screen"""
        text_interface.send_message(constants.ENTER_TOWN_MESSAGE)
        