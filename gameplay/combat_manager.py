import utils.constants as constants

class CombatManager:

    def is_combat_over(self, player, enemy) -> bool:
        return not (player.is_alive() and enemy.is_alive())

    def do_combat(self, player, enemy, text_interface, registries):
        player.card_manager.reset_cards()
        player.card_manager.shuffle()
        enemy.card_manager.shuffle()
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
        combatant.reset_for_turn()
        combatant.card_manager.draw_hand()

        combatant.status_manager.trigger_statuses_on_turn(combatant, registries.statuses)
        if self.is_combat_over(combatant, opponent):
            return True

        combatant.status_manager.decrement_statuses()
        combatant.replenish_resources_for_turn()
        return False

    def do_player_action(self, player, enemy, text_interface, registries):
        selection = text_interface.turn_options_prompt()
        if selection < 0:  # Pass turn
            return True
        if selection >= len(player.card_manager.hand):
            return False
        card = player.card_manager.hand[selection]
        self.play_card(player, enemy, card, text_interface, registries)
        return self.is_combat_over(player, enemy)

    def play_card(self, combatant, opponent, card, text_interface, registries):
        resource = constants.Resources.STAMINA
        if card.card_type == constants.CardTypes.SPELL.name:
            resource = constants.Resources.MAGICKA
        if not combatant.resources[resource.name].try_spend(card.get_cost()):
            text_interface.send_message("Not enough " + resource.value)
            return

        combatant.card_manager.discard(card)
        
        for effect_id, effect_level in card.effects.items():
            effect = registries.effects.get_effect(effect_id)
            level = effect_level.modified_level
            effect.resolve(combatant, opponent, level, status_registry=registries.statuses)

        text_interface.send_message(constants.CARD_PLAYED_MESSAGE.format(combatant.name, card.name, opponent.name, opponent.get_health()))

    def do_enemy_turn(self, player, enemy, text_interface, registries):
        self.beginning_of_turn(enemy, player, registries)
        playable_card_exists = True
        while playable_card_exists and not self.is_combat_over(player, enemy):
            playable_card_exists = False
            for card in enemy.card_manager.hand:
                if card.cost <= enemy.get_stamina(): ###
                    playable_card_exists = True
                    self.play_card(enemy, player, card, text_interface, registries)
                    if self.is_combat_over(player, enemy):
                        return
                    break
        text_interface.send_message(constants.ENEMY_PASSES_MESSAGE.format(enemy.name))
        enemy.card_manager.discard_hand()
