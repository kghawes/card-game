"""
This module defines the TextInterface class, the text-based UI.
"""
import sys
from functools import partial
import utils.constants as constants

class TextInterface:
    """
    This class prints messages and receives input from the user.
    """
    def send_message(self, message):
        """
        Display a message to the user.
        """
        print(message)

    def name_prompt(self) -> str:
        """
        Prompt the user for the player name.
        """
        response = ""
        while not response or len(response) > constants.MAX_NAME_LENGTH:
            response = input(constants.PROMPT_NAME)
        return response

    def level_up_prompt(self, player) -> str:
        """
        Prompt the user to choose a resource to increase.
        """
        print(f"LEVEL UP! You are now level {player.level}!")
        response = ""
        while True:
            response = input("Increase HEALTH, STAMINA, or MAGICKA? ").upper()
            if response in player.resources:
                return response

    def display_turn_info(self, player, enemy, effect_registry):
        """
        Show the turn 'screen' with current stats and cards in hand.
        """
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
            print(f"{idx}. {card.name} ({card.card_type})")
            print(f"     Cost: {card.get_cost()}")
            for effect_id, effect_level in card.effects.items():
                effect = effect_registry.get_effect(effect_id)
                level = effect_level.get_level()
                print(f"     * {effect.name} {level} *")

        # Divider and status display
        print(constants.TEXT_DIVIDER)
        print("Active Statuses:")
        for status_id, level in player.status_manager.statuses.items():
            print(f"  {status_id}: Level {level}")

        print(constants.TEXT_DIVIDER)

    def turn_options_prompt(self, player, enemy, registries, card_cache) -> int:
        """
        Prompt the user for an action during their turn.
        """
        debug_commands = self.debug_setup(registries.effects)

        while True:
            response = input(constants.PROMPT_TURN_OPTIONS).strip()

            # Handle debug commands starting with '/'
            if response.startswith('/'):
                command, *args = response[1:].split(' ', 1)
                arg = args[0] if args else ""
                if command in debug_commands:
                    debug_commands[command](arg, player, enemy, registries, card_cache)
                    self.display_turn_info(player, enemy, registries.effects)
                else:
                    print("Unknown command.")
                continue

            # Normal game commands
            if response.isdigit():
                return int(response)
            if response.upper() == constants.INPUT_PASS_TURN:
                return -1

            print("Invalid input.")

        raise RuntimeError("Unexpected state: Exited loop without returning.")

    def parse_effect_input(self, input_str):
        """
        Parse the user input to extract effect ID and level.
        """
        parts = input_str.strip().rsplit(' ', 1)
        effect_id = parts[0].replace(" ", "_").upper()
        level = int(parts[1])
        return effect_id, level

    def debug_setup(self, effect_registry) -> dict:
        """
        Define debug commands usable from the turn options prompt.
        """
        debug_commands = {
            "q": lambda _, __, ___, ____, _____: sys.exit(0),  # Quit command
            "e": lambda args, p, e, r, _: self.handle_effect_command(args, p, e, r),  # Effect command
            "c": lambda args, p, _, __, c: self.handle_card_command(args, p, c) # Card command
        }

        # Add effect commands dynamically
        for effect_id, effect in effect_registry.effects.items():
            debug_commands[effect_id] = partial(
                self.apply_effect_debug, effect
            )

        return debug_commands

    def handle_effect_command(self, args, player, enemy, registries):
        """
        Handle the '/e' debug command for resolving effects.
        """
        effect_id, level = self.parse_effect_input(args)
        effect = registries.effects.get_effect(effect_id)
        effect.resolve(player, enemy, level, registries.statuses)
        print(f"Resolved {effect.name} at level {level}")

    def apply_effect_debug(self, effect, player, enemy, level, status_registry):
        """
        Resolve an effect for debugging purposes.
        """
        effect.resolve(player, enemy, level, status_registry=status_registry)
        print(f"Resolved {effect.name} at level {level}")

    def handle_card_command(self, card_id, player, card_cache):
        """
        Handle the '/c' debug command for adding cards.
        """
        card = card_cache.create_card(card_id.upper())
        player.card_manager.hand.append(card)
