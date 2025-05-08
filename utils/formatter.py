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
        card_strings = []
        tooltip_strings = []

        for leveled_effect in effects:
            effect = leveled_effect.reference
            name = effect.name
            level = leveled_effect.get_level()
            description = effect.description

            if hasattr(effect, 'status_ref'):
                # For status effects, use the status description instead
                status = effect.status_ref
                use_generic = effect.matches("REMOVE")
                description = self.format_status_data(status, level, use_generic=use_generic)
            else:
                description = description.format(level=level)

            tooltip_line = f"{name} {level}:\n{description}"
            card_line = f"{name} {level}"

            tooltip_strings.append(tooltip_line)
            card_strings.append(card_line)

        formatted_strings = {
            'card_text': '\n'.join(card_strings),
            'tooltip_text': '\n'.join(tooltip_strings)
        }
        return formatted_strings

    def format_status_data(self, status, level, use_generic=False) -> str:
        """
        Format the status data for display.
        """
        description = status.description

        if use_generic:
            return description.format(
                level="X",
                percent_change="X%",
                evasion_probability="X%",
                crit_probability="X%"
            )

        evasion_probability = c.BASE_EVASION_PROBABILITY * level
        crit_probability = c.BASE_CRIT_PROBABILITY * level
        percent_change = c.SCALE_FACTOR * level

        return description.format(
            level=level,
            percent_change=f"{percent_change}%",
            evasion_probability=f"{int(evasion_probability * 100)}%",
            crit_probability=f"{int(crit_probability * 100)}%"
        )
