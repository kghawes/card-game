"""This module defines the Formatter class"""
import utils.constants as c

class Formatter:
    """
    This class is responsible for formatting strings and data for display.
    """
    def format_effect_data(self, effects) -> dict:
        """
        Format the effect data for display.
        """
        formatted_data = { }
        for leveled_effect in effects:
            name = leveled_effect.reference.name
            level = leveled_effect.get_level()
            description = leveled_effect.reference.description

        return formatted_data

    def format_status_data(self, leveled_status) -> str:
        """
        Format the status data for display.
        """
        status = leveled_status.reference
        name = status.name
        level = leveled_status.get_level()
        description = status.description
        #
