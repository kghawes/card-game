"""This module defines the Formatter class"""
import utils.constants as c
import re

class Formatter:
    """
    This class is responsible for formatting strings and data for display.
    """
    def format_effect_data(self, effects, card=None, owner=None, attribute_registry=None) -> dict:
        """
        Format the effect data for display.
        """
        card_strings = [ ]
        tooltip_strings = [ ]

        for leveled_effect in effects:
            effect = leveled_effect.reference
            name = effect.name
            level = leveled_effect.get_level(card, owner, attribute_registry)
            description = effect.description
            tooltip_line = f"{name} level {level}"
            tooltip_line = self.apply_font_color(tooltip_line, 'ffffff')

            if hasattr(effect, 'status_ref'):
                status = effect.status_ref
                is_remove = effect.matches(c.EffectNames.REMOVE.name)
                is_player = effect.target_type_enum.name == c.TargetTypes.SELF.name
                description = self.format_status_data(
                    status, level, use_generic=is_remove, is_player=is_player
                    )
                if is_remove:
                    tooltip_line = f"{tooltip_line}\n({status.name}: {description})"
                else:
                    tooltip_line = f"{tooltip_line}:\n{description}"
            elif description:
                description = description.format(level=self.apply_font_color(level, '6486ff'))
                tooltip_line = f"{tooltip_line}:\n{description}"                

            card_line = f"{name} {level}"

            tooltip_strings.append(tooltip_line)
            card_strings.append(card_line)

        formatted_strings = {
            'card_text': '\n'.join(card_strings),
            'tooltip_text': '\n\n'.join(tooltip_strings)
        }
        return formatted_strings

    def format_status_data(self, status, level, use_generic=False, is_player=True) -> str:
        """
        Format the status data for display.
        """
        description = status.description

        if use_generic:
            values = {
                'level': 'X',
                'percent_change': 'X%',
                'evasion_probability': 'X%',
                'crit_probability': 'X%'
            }
        else:
            values = {
                'level': level,
                'percent_change': f"{int(c.SCALE_FACTOR * level * 100)}%",
                'evasion_probability': f"{int(c.BASE_EVASION_PROBABILITY * level * 100)}%",
                'crit_probability': f"{int(c.BASE_CRIT_PROBABILITY * level * 100)}%"
            }
        
        for key, value in values.items():
            values[key] = self.apply_font_color(value, '6486ff')

        description = self.subjectify(description, is_player)
        description = description.format(**values)
        return description

    def subjectify(self, text, is_player):
        """
        Replace conditional subject forms like {you|the enemy} based on subject.
        """
        def repl(match):
            left, right = match.group(1).split('|', 1)
            return left if is_player else right
        return re.sub(r'\{([^{}|]+?\|[^{}|]+?)\}', repl, text)
    
    def apply_font_color(self, text, color):
        """
        Apply font color to the text. Color should be a hex string without the #, e.g. 'ff0000' for red.
        """
        return f"[color={color}]{text}[/color]"
