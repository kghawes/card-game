"""
This module defines the TextInterface class, the text-based UI.
"""
import sys
from functools import partial
import traceback
import utils.constants as c

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
        while not response or len(response) > c.MAX_NAME_LENGTH:
            print(c.PROMPT_NAME)
            response = input(">  ")
        return response

    def level_up_prompt(self, player) -> str:
        """
        Prompt the user to choose a resource to increase.
        """
        print(f"LEVEL UP! You are now level {player.level}!")
        response = ""
        while True:
            print("Increase HEALTH, STAMINA, or MAGICKA?")
            response = input(">  ").upper()
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
        print(c.TEXT_DIVIDER)
        print(f"\033[01m{enemy.name:<{name_padding}}\033[0m HP: {enemy.get_health():>{max_hp_length}}/{enemy.get_max_health():<{max_hp_length}}  Deck: {len(enemy.card_manager.deck):<5} Discard: {len(enemy.card_manager.discard_pile):<5}")
        print(f"\033[01m{player.name:<{name_padding}}\033[0m HP: {player.get_health():>{max_hp_length}}/{player.get_max_health():<{max_hp_length}}  Deck: {len(player.card_manager.deck):<5} Discard: {len(player.card_manager.discard_pile):<5}")
        print(c.TEXT_DIVIDER)
        print(f"Stamina: {player.get_stamina()}/{player.get_max_stamina():<{hp_padding}}  Magicka: {player.get_magicka()}/{player.get_max_magicka()}")
        print()

        self.display_hand(player, effect_registry)

        # Divider and status display
        print(c.TEXT_DIVIDER)
        print("Active Statuses:")
        for status_id, level in player.status_manager.statuses.items():
            print(f"  {status_id}: Level {level}")

        print(c.TEXT_DIVIDER)

    def turn_options_prompt(self, player, enemy, registries, card_cache) -> int:
        """
        Prompt the user for an action during their turn.
        """
        debug_commands = self.debug_setup(registries.effects)

        while True:
            print(c.PROMPT_TURN_OPTIONS)
            response = input(">  ").strip()

            if response.startswith('/'):
                command, *args = response[1:].split(' ', 1)
                arg = args[0] if args else ""
                if command in debug_commands:
                    try:
                        debug_commands[command](arg, player, enemy, registries, card_cache)
                        self.display_turn_info(player, enemy, registries.effects)
                    except Exception:
                        print(traceback.format_exc())
                else:
                    print("Unknown command.")
                continue

            # Normal game commands
            if response.isdigit():
                return int(response)
            if response.upper() == c.INPUT_PASS_TURN:
                return -1

            print("Invalid input.")

        raise RuntimeError("Unexpected state: Exited loop without returning.")

    def display_hand(self, player, effect_registry):
        """
        Display player's hand with card effects.
        """
        print("\033[01mCards in Hand:\033[0m")
        for idx, card in enumerate(player.card_manager.hand):
            print(f"{idx}. {card.name} ({card.card_type} - {card.subtype})")
            print(f"     Cost: {card.get_cost()}")
            for effect_id, effect_level in card.effects.items():
                effect = effect_registry.get_effect(effect_id)
                level = effect_level.get_level()
                print(f"     * {effect.name} {level} *")

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

    def discard_prompt(
            self, player, count, is_optional, effect_registry
            ) -> list:
        """
        Prompt the user for a list of cards to discard and redraw.
        """
        if count <= 0:
            return

        self.display_hand(player, effect_registry)
        print()
        prompt = "List{} {} cards to discard."
        if is_optional:
            prompt = prompt.format(" up to", count)
        else:
            prompt = prompt.format("", count)
        indices = []
        while True:
            print(prompt)
            response = input(">  ")
            selected_indices = [idx.strip() for idx in response.split(",")]
            if (is_optional and len(selected_indices) > count) or \
                (not is_optional and len(selected_indices) != count) or \
                    len(selected_indices) <= 0:
                    continue
            try:
                hand = player.card_manager.hand
                indices = self.get_card_indices(selected_indices, len(hand)-1)
                break
            except IndexError:
                print("TEST: discard_prompt raised IndexError.")
                continue
        return indices

    def get_card_indices(self, selected_indices, max_index) -> list:
        """
        Parse player input as a list of card indices.
        """
        indices = []
        for selection in selected_indices:
            index = -1
            selection = selection.strip()
            if selection.isdigit():
                index = int(selection)
            else:
                raise IndexError
            if index > max_index or index < 0:
                raise IndexError
            if index in indices:
                raise IndexError
            indices.append(index)
        return indices

    def return_from_discard_prompt(self, discard_pile, count) -> list:
        """
        Prompt the user for cards to take from discard pile.
        """
        selection = []
        if count <= 0 or len(discard_pile) <= 0:
            return selection
        if count >= len(discard_pile) and count <= c.MAX_HAND_SIZE:
            return discard_pile
        print("Discard Pile:")
        for idx, card in enumerate(discard_pile):
            print(f"{idx}. {card.name}")
        while True:
            print(f"Select up to {count} cards to return to your hand:")
            response = input(">  ")
            selected_indices = response.split(",")
            if len(selected_indices) > min(count, c.MAX_HAND_SIZE):
                continue
            max_index = len(discard_pile) - 1
            try:
                selection = self.get_card_indices(selected_indices, max_index)
                break
            except IndexError:
                continue
        return selection

    def card_reward_prompt(self, card, effect_registry) -> bool:
        """
        Prompt the user to take or leave the card.
        """
        print(f"You got {card.name}!")
        card_type_string = card.card_type
        if card.subtype:
            card_type_string += f" [{card.subtype}]"
        print(f"({card_type_string} - Cost: {card.get_cost()} - Value: {card.value}g)")
        for effect_id, effect_level in card.effects.items():
            effect = effect_registry.get_effect(effect_id)
            level = effect_level.get_level()
            print(f"* {effect.name} {level} *")
        print()
        while True:
            print("Keep this card? (Y/N)")
            response = input(">  ").upper().strip()
            if response not in ("Y", "N"):
                continue
            if response == "Y":
                return True
            if response == "N":
                print("Are you sure you want to leave this card? (Y/N)")
                confirmation = input(">  ").upper().strip()
                if confirmation not in ("Y", "N") or confirmation == "N":
                    continue
                if confirmation == "Y":
                    return False

    def rewards_message(self, gold, exp):
        """
        Inform the player how much gold and experience they received.
        """
        print(f"You found {gold} gold!")
        print(f"You got {exp} experience points!")
