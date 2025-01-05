"""
This Module defines the CombatManager class.
"""
import utils.constants as c
from core.statuses import FilterEffectStatus

class CombatManager:
    """This class controls the flow of combat and coordinates between
    combatants, statuses, and effects."""

    def is_combat_over(self, player, enemy) -> bool:
        """Check if either combatant is dead."""
        return not (player.is_alive() and enemy.is_alive())

    def do_combat(self, player, enemy, text_interface, registries):
        """Enter the combat loop."""
        player.card_manager.shuffle()
        enemy.card_manager.shuffle()
        while True:
            self.do_player_turn(player, enemy, text_interface, registries)
            if self.is_combat_over(player, enemy):
                break
            self.do_enemy_turn(player, enemy, text_interface, registries)
            if self.is_combat_over(player, enemy):
                break
        player.status_manager.reset_statuses()
        player.modifier_manager.reset_all()

    def do_player_turn(self, player, enemy, text_interface, registries):
        """Prepare for the player to take their turn then handle any
        actions they perform."""
        if self.beginning_of_turn(player, enemy, registries.statuses):
            return
        turn_ended = False
        while not turn_ended and not self.is_combat_over(player, enemy):
            text_interface.display_turn_info(player, enemy, registries.effects)
            turn_ended = self.do_player_action(
                player, enemy, text_interface, registries
                )
        self.end_of_turn(player, registries.statuses)

    def beginning_of_turn(self, combatant, opponent, status_registry) -> bool:
        """Handle resetting resources, triggering statuses, and drawing
        cards. Returns whether combat ended during the beginning phase."""
        combatant.reset_for_turn()

        combatant.card_manager.draw_hand(combatant.modifier_manager)

        combatant.status_manager.trigger_statuses_on_turn(
            combatant, status_registry
            )
        if self.is_combat_over(combatant, opponent):
            return True

        # Ensure modifiers are recalculated after status updates
        combatant.modifier_manager.recalculate_all_effects(
            status_registry, combatant.card_manager
            )

        combatant.replenish_resources_for_turn()
        return False

    def end_of_turn(self, combatant, status_registry):
        """Discard hand and decrement active status levels."""
        combatant.card_manager.discard_hand()
        combatant.status_manager.decrement_statuses(
            combatant, status_registry
            )

    def do_player_action(self, player, enemy, text_interface, registries):
        """Get the player input and perform the selected action."""
        selection = text_interface.turn_options_prompt(
            player, enemy, registries
            )
        if selection < 0:  # Pass turn
            return True
        if selection >= len(player.card_manager.hand):
            return False
        card = player.card_manager.hand[selection]
        self.play_card(player, enemy, card, text_interface, registries)
        return self.is_combat_over(player, enemy)

    def play_card(self, combatant, opponent, card, text_interface, registries):
        """Activate a card's effects, spend its cost, and discard it."""
        resource_id = c.Resources.STAMINA.name
        if card.card_type == c.CardTypes.SPELL.name:
            resource = c.Resources.MAGICKA
        if not combatant.resources[resource_id].try_spend(card.get_cost()):
            text_interface.send_message("Not enough " + resource.value)
            return

        for effect_id, effect_level in card.effects.items():
            if not self.effect_can_resolve(combatant, effect_id):
                continue
            effect = registries.effects.get_effect(effect_id)
            level = effect_level.get_level()
            effect.resolve(
                combatant, opponent, level, status_registry=registries.statuses
                )

        combatant.card_manager.discard(card)

        text_interface.send_message(c.CARD_PLAYED_MESSAGE.format(
            combatant.name, card.name, opponent.name, opponent.get_health())
            )

    def effect_can_resolve(self, combatant, effect_id) -> bool:
        """Check if the given card effect can resolve based on current
        status effects."""
        for status in combatant.status_manager.statuses.values():
            if isinstance(status, FilterEffectStatus):
                if not status.effect_can_resolve(effect_id):
                    return False
        return True

    def do_enemy_turn(self, player, enemy, text_interface, registries):
        """Process enemy actions."""
        self.beginning_of_turn(enemy, player, registries.statuses)
        playable_card_exists = True
        while playable_card_exists and not self.is_combat_over(player, enemy):
            playable_card_exists = False
            for card in enemy.card_manager.hand:
                if card.cost <= enemy.get_stamina(): ###
                    playable_card_exists = True
                    self.play_card(
                        enemy, player, card, text_interface, registries
                        )
                    if self.is_combat_over(player, enemy):
                        return
                    break
        text_interface.send_message(c.ENEMY_PASSES_MESSAGE.format(enemy.name))
        self.end_of_turn(enemy, registries.statuses)
