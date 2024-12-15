import utils.constants as constants

class Town:
    def enter_town(self, text_interface):
        text_interface.send_message(constants.ENTER_TOWN_MESSAGE)
        