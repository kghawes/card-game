import utils.constants as constants

class CombatManager:

    def is_combat_over(self, player, enemy) -> bool:
        return not (player.is_alive() and enemy.is_alive())

    def do_combat(self, player, enemy, text_interface, status_registry, effect_registry):
        while True:
            self.do_player_turn(player, enemy, text_interface, status_registry, effect_registry)
            if self.is_combat_over(player, enemy):
                return
            self.do_enemy_turn(player, enemy, text_interface, status_registry, effect_registry)
            if self.is_combat_over(player, enemy):
                return

    def do_player_turn(self, player, enemy, text_interface, status_registry, effect_registry):
        if self.beginning_of_turn(player, enemy, status_registry):
            return
        turn_ended = False
        while not turn_ended and not self.is_combat_over(player, enemy):
            text_interface.display_turn_info(player, enemy, effect_registry)
            turn_ended = self.do_player_action(player, enemy, text_interface, effect_registry)
        player.card_manager.discard_hand()

    def beginning_of_turn(self, combatant, opponent, status_registry):
        combatant.card_manager.shuffle()
        combatant.card_manager.draw()

        combatant.status_manager.trigger_statuses(combatant, status_registry)
        if self.is_combat_over(combatant, opponent):
            return True

        combatant.status_manager.decrement_statuses()
        combatant.replenish_stamina()
        combatant.replenish_magicka()
        return False

    def do_player_action(self, player, enemy, text_interface, effect_registry):
        selection = text_interface.turn_options_prompt()
        if selection < 0:  # Pass turn
            return True
        if selection >= len(player.card_manager.hand):
            return False
        card = player.card_manager.hand[selection]
        if card.cost > player.stamina:
            text_interface.send_message(constants.NOT_ENOUGH_STAMINA_MESSAGE)
            return False
        self.play_card(player, enemy, card, text_interface, effect_registry)
        return self.is_combat_over(player, enemy)

    def play_card(self, combatant, opponent, card, text_interface, effect_registry):
        combatant.card_manager.discard(card)
        combatant.try_spend_stamina(card.cost)

        for effect_id, effect_level in card.effects.items():
            effect = effect_registry.get_effect(effect_id)
            effect.resolve(combatant, opponent, effect_level)

        text_interface.send_message(constants.CARD_PLAYED_MESSAGE.format(
            combatant.name, card.name, opponent.name, opponent.health
        ))

    def do_enemy_turn(self, player, enemy, text_interface, status_registry, effect_registry):
        self.beginning_of_turn(enemy, player, status_registry)
        playable_card_exists = True
        while playable_card_exists and not self.is_combat_over(player, enemy):
            playable_card_exists = False
            for card in enemy.card_manager.hand:
                if card.cost <= enemy.stamina:
                    playable_card_exists = True
                    self.play_card(enemy, player, card, text_interface, effect_registry)
                    if self.is_combat_over(player, enemy):
                        return
                    break
        text_interface.send_message(constants.ENEMY_PASSES_MESSAGE.format(enemy.name))
        enemy.card_manager.discard_hand()
