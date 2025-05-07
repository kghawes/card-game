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
        card_strings = [ ]
        tooltip_strings = [ ]

        for leveled_effect in effects:
            effect = leveled_effect.reference
            name = effect.name
            level = leveled_effect.get_level()
            description = effect.description
            if hasattr(effect, 'status_ref'):
                # Apply and Remove Status-type effects
                status = effect.status_ref
                target = effect.target_type_enum.value
                status_description = self.format_status_data(status, level)
                description = description.format(
                    level=level,
                    status_name=status.name,
                    target=target,
                    status_description=status_description
                )
            else:
                description = description.format(level=level)
            card_strings.append(f"{name} {level}")
            tooltip_strings.append(f"{name} {level}: {description}")

        formatted_strings = {
            'card_text': '\n'.join(card_strings),
            'tooltip_text': '\n'.join(tooltip_strings)
        }
        return formatted_strings

    def format_status_data(self, status, level) -> str:
        """
        Format the status data for display.
        """
        name = status.name
        description = status.description
        # description strings
        evasion_probability = c.BASE_EVASION_PROBABILITY * level
        crit_probability = c.BASE_CRIT_PROBABILITY * level
        percent_change = c.SCALE_FACTOR * level
        description = description.format(
            level=level,
            percent_change=percent_change,
            evasion_probability=evasion_probability,
            crit_probability=crit_probability
        )
        return f"{name} (Level {level}): {description}"
