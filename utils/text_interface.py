import utils.constants as constants

class TextInterface:
    def send_message(self, message):
        print(message)

    def name_prompt(self):
        response = ""
        while not response or len(response) > constants.MAX_NAME_LENGTH:
            response = input(constants.PROMPT_NAME)
        return response

    def display_turn_info(self, enemy, player):
        print(constants.DISPLAY_TURN_INFO.format(
            constants.TEXT_DIVIDER,
            enemy.name, enemy.health, enemy.max_health,
            len(enemy.card_manager.deck), len(enemy.card_manager.discard_pile),
            constants.TEXT_DIVIDER,
            player.name, player.health, player.max_health,
            player.stamina, player.max_stamina,
            len(player.card_manager.deck), len(player.card_manager.discard_pile)
        ))
        for idx, card in enumerate(player.card_manager.hand):
            print(constants.DISPLAY_CARD.format(idx, card.name, card.cost, card.damage))
        print(constants.TEXT_DIVIDER)

    def turn_options_prompt(self):
        while True:
            response = input(constants.PROMPT_TURN_OPTIONS).strip()
            if response.isdigit():
                return int(response)
            elif response.upper() == constants.INPUT_PASS_TURN:
                return -1