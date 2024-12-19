import utils.constants as constants

class CombatManager:

    def is_combat_over(self, player, enemy) -> bool:
        return not (player.is_alive() and enemy.is_alive())

    def do_combat(self, player, enemy, text_interface, registries):
        while True:
            self.do_player_turn(player, enemy, text_interface, registries)
            if self.is_combat_over(player, enemy):
                return
            self.do_enemy_turn(player, enemy, text_interface, registries)
            if self.is_combat_over(player, enemy):
                return

    def do_player_turn(self, player, enemy, text_interface, registries):
        if self.beginning_of_turn(player, enemy, registries):
            return
        turn_ended = False
        while not turn_ended and not self.is_combat_over(player, enemy):
            text_interface.display_turn_info(player, enemy, registries.effects)
            turn_ended = self.do_player_action(player, enemy, text_interface, registries)
        player.card_manager.discard_hand()

    def beginning_of_turn(self, combatant, opponent, registries):
        combatant.card_manager.shuffle()
        combatant.card_manager.draw()

        combatant.status_manager.trigger_statuses_on_turn(combatant, registries.statuses)
        if self.is_combat_over(combatant, opponent):
            return True

        combatant.status_manager.decrement_statuses()
        combatant.replenish_stamina()
        combatant.replenish_magicka()
        return False

    def do_player_action(self, player, enemy, text_interface, registries):
        selection = text_interface.turn_options_prompt()
        if selection < 0:  # Pass turn
            return True
        if selection >= len(player.card_manager.hand):
            return False
        card = player.card_manager.hand[selection]
        if card.cost > player.stamina:
            text_interface.send_message(constants.NOT_ENOUGH_STAMINA_MESSAGE)
            return False
        self.play_card(player, enemy, card, text_interface, registries)
        return self.is_combat_over(player, enemy)

    def play_card(self, combatant, opponent, card, text_interface, registries):
        combatant.card_manager.discard(card)
        combatant.try_spend_resource(constants.Resources.STAMINA.value.attribute_name, card.cost)

        for effect_id, effect_level in card.effects.items():
            effect = registries.effects.get_effect(effect_id)
            effect.resolve(combatant, opponent, effect_level, status_registry=registries.statuses)
            if self.is_combat_over(combatant, opponent):
                return

        text_interface.send_message(constants.CARD_PLAYED_MESSAGE.format(
            combatant.name, card.name, opponent.name, opponent.health
        ))

    def do_enemy_turn(self, player, enemy, text_interface, registries):
        self.beginning_of_turn(enemy, player, registries)
        playable_card_exists = True
        while playable_card_exists and not self.is_combat_over(player, enemy):
            playable_card_exists = False
            for card in enemy.card_manager.hand:
                if card.cost <= enemy.stamina:
                    playable_card_exists = True
                    self.play_card(enemy, player, card, text_interface, registries)
                    if self.is_combat_over(player, enemy):
                        return
                    break
        text_interface.send_message(constants.ENEMY_PASSES_MESSAGE.format(enemy.name))
        enemy.card_manager.discard_hand()
