import utils.constants as constants

class TextInterface:
    def send_message(self, message):
        print(message)

    def name_prompt(self):
        response = ""
        while not response or len(response) > constants.MAX_NAME_LENGTH:
            response = input(constants.PROMPT_NAME)
        return response
        
    def display_turn_info(self, player, enemy, effect_registry):
        # Calculate dynamic widths based on the longest name and health value lengths
        name_padding = max(len(enemy.name), len(player.name)) + 2
        max_hp_length = max(len(str(enemy.max_health)), len(str(player.max_health)))
        hp_padding = 4 + max_hp_length * 2  # Include space for "HP: X/Y" where X and Y can vary in length
    
        # Header with enemy and player stats
        print(constants.TEXT_DIVIDER)
        print(f"\033[01m{enemy.name:<{name_padding}}\033[0m HP: {enemy.health:>{max_hp_length}}/{enemy.max_health:<{max_hp_length}}  Deck: {len(enemy.card_manager.deck):<5} Discard: {len(enemy.card_manager.discard_pile):<5}")
        print(f"\033[01m{player.name:<{name_padding}}\033[0m HP: {player.health:>{max_hp_length}}/{player.max_health:<{max_hp_length}}  Deck: {len(player.card_manager.deck):<5} Discard: {len(player.card_manager.discard_pile):<5}")
        print(constants.TEXT_DIVIDER)
        print(f"Stamina: {player.stamina}/{player.max_stamina:<{hp_padding}}  Magicka: {player.magicka}/{player.max_magicka}")
        print()
        # Display player's hand with card effects
        print("\033[01mCards in Hand:\033[0m")
        for idx, card in enumerate(player.card_manager.hand):
            print(f"{idx}. {card.name} (Cost: {card.cost})")
            for effect_id, effect_level in card.effects.items():
                effect = effect_registry.get_effect(effect_id)
                print(f"     Level {effect_level} {effect.name}")
    
        # Divider and status display
        print(constants.TEXT_DIVIDER)
        print("Active Statuses:")
        for status_id, level in player.status_manager.statuses.items():
            print(f"  {status_id}: Level {level}")
    
        print(constants.TEXT_DIVIDER)

    def turn_options_prompt(self):
        while True:
            response = input(constants.PROMPT_TURN_OPTIONS).strip()
            if response.isdigit():
                return int(response)
            elif response.upper() == constants.INPUT_PASS_TURN:
                return -1