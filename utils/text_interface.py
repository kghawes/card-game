"""This module defines the TextInterface class, the text-based UI."""
import sys
from functools import partial
import utils.constants as constants

class TextInterface:
    """This class prints messages and receives input from the user."""
    def send_message(self, message):
        """Display a message to the user."""
        print(message)

    def name_prompt(self) -> str:
        """Prompt the user for the player name."""
        response = ""
        while not response or len(response) > constants.MAX_NAME_LENGTH:
            response = input(constants.PROMPT_NAME)
        return response

    def display_turn_info(self, player, enemy, effect_registry):
        """Show the turn 'screen' with current stats and cards in hand."""
        # Calculate dynamic widths based on the longest name and health
        # value lengths
        name_padding = max(len(enemy.name), len(player.name)) + 2
        max_hp_length = max(
            len(str(enemy.get_max_health())),
            len(str(player.get_max_health()))
            )
        hp_padding = 4 + max_hp_length * 2
        # Include space for "HP: X/Y" where X and Y can vary in length

        # Header with enemy and player stats
        print(constants.TEXT_DIVIDER)
        print(f"\033[01m{enemy.name:<{name_padding}}\033[0m HP: {enemy.get_health():>{max_hp_length}}/{enemy.get_max_health():<{max_hp_length}}  Deck: {len(enemy.card_manager.deck):<5} Discard: {len(enemy.card_manager.discard_pile):<5}")
        print(f"\033[01m{player.name:<{name_padding}}\033[0m HP: {player.get_health():>{max_hp_length}}/{player.get_max_health():<{max_hp_length}}  Deck: {len(player.card_manager.deck):<5} Discard: {len(player.card_manager.discard_pile):<5}")
        print(constants.TEXT_DIVIDER)
        print(f"Stamina: {player.get_stamina()}/{player.get_max_stamina():<{hp_padding}}  Magicka: {player.get_magicka()}/{player.get_max_magicka()}")
        print()
        # Display player's hand with card effects
        print("\033[01mCards in Hand:\033[0m")
        for idx, card in enumerate(player.card_manager.hand):
            print(f"{idx}. {card.name} (Cost: {card.cost})")
            for effect_id, effect_level in card.effects.items():
                effect = effect_registry.get_effect(effect_id)
                level = effect_level.get_level()
                print(f"     Level {level} {effect.name}")
    
        # Divider and status display
        print(constants.TEXT_DIVIDER)
        print("Active Statuses:")
        for status_id, level in player.status_manager.statuses.items():
            print(f"  {status_id}: Level {level}")
    
        print(constants.TEXT_DIVIDER)

    def turn_options_prompt(self, player, enemy, registries) -> int:
        """Prompt the user for an action during their turn."""
        debug_commands = self.debug_setup(player, enemy, registries.effects)
        
        while True:
            response = input(constants.PROMPT_TURN_OPTIONS).strip()
            if response.isdigit():
                return int(response)
            response = response.upper()
            if response == constants.INPUT_PASS_TURN:
                return -1
            elif response in debug_commands:
                debug_commands[response]()
            else:
                effect_id, level = self.parse_effect_input(response)
                if effect_id in debug_commands:
                    debug_commands[effect_id](
                        player, enemy, level, registries.statuses
                        )
                    self.display_turn_info(player, enemy, registries.effects)
        
        raise RuntimeError("Unexpected state: Exited loop without returning.")
    
    def parse_effect_input(self, input_str):
        """If the user input the name of an effect an a level, parse
        the information so that the effect can be resolved."""
        parts = input_str.strip().split()
    
        level = int(parts.pop())
        effect_id = "_".join(parts)
    
        return effect_id, level

    def debug_setup(self, player, enemy, effect_registry) -> dict:
        """Define debug commands usable from the turn options prompt."""
        debug_commands = {
            "QUIT": lambda: sys.exit(0)
        }
        
        for effect_id, effect in effect_registry.effects.items():
            # Use partial to capture the specific effect at loop iteration time
            debug_commands[effect_id] = partial(
                self.apply_effect_debug, effect
                )
    
        return debug_commands
    
    def apply_effect_debug(
            self, effect, player, enemy, level, status_registry
            ):
        """Resolve the debug effect."""
        effect.resolve(player, enemy, level, status_registry=status_registry)
        print(f"Resolved {effect.name}")
