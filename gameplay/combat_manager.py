import utils.constants as constants

class CombatManager:
    def is_combat_over(self, player, enemy) -> bool:
        return not (player.is_alive() and enemy.is_alive())

    def do_combat(self, player, enemy, text_interface) -> bool:
        while True:
            self.do_player_turn(player, enemy, text_interface)
            if self.is_combat_over(player, enemy):
                break
            self.do_enemy_turn(player, enemy, text_interface)
            if self.is_combat_over(player, enemy):
                break
        return player.is_alive()

    def do_player_turn(self, player, enemy, text_interface):
        self.beginning_of_turn(player)
        text_interface.display_turn_info(player, enemy)
        turn_ended = False
        while not turn_ended:
            turn_ended = self.do_player_action(player, enemy, text_interface)
        player.card_manager.discard_hand()

    def beginning_of_turn(self, combatant):
        combatant.card_manager.shuffle()
        combatant.card_manager.draw()
        combatant.replenish_stamina()

    def do_player_action(self, player, enemy, text_interface) -> bool:
        selection = text_interface.turn_options_prompt()
        if selection < 0:
            return True
        if selection >= len(player.card_manager.hand):
            return False
        card = player.card_manager.hand[selection]
        if card.cost > player.stamina:
            text_interface.send_message(constants.NOT_ENOUGH_STAMINA_MESSAGE)
            return False
        if self.play_card(player, enemy, card, text_interface):
            return True
        text_interface.display_turn_info(player, enemy)
        return False

    def play_card(self, combatant, opponent, card, text_interface) -> bool:
        combatant.card_manager.discard(card)
        combatant.try_spend_stamina(card.cost)
        opponent.take_damage(card.damage, "")
        text_interface.send_message(constants.CARD_PLAYED_MESSAGE.format(
            combatant.name, card.name, opponent.name, opponent.health
        ))
        return not opponent.is_alive()

    def do_enemy_turn(self, player, enemy, text_interface):
        self.beginning_of_turn(enemy)
        playable_card_exists = True
        while playable_card_exists:
            playable_card_exists = False
            for card in enemy.card_manager.hand:
                if card.cost <= enemy.stamina:
                    playable_card_exists = True
                    if self.play_card(enemy, player, card, text_interface):
                        return
                    break
        text_interface.send_message(constants.ENEMY_PASSES_MESSAGE.format(enemy.name))
        enemy.card_manager.discard_hand()