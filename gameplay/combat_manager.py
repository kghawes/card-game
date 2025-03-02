"""
This Module defines the CombatManager class.
"""
import utils.constants as c
from core.statuses import FilterEffectStatus, RestrictCardTypeStatus, LimitCardPlayStatus

class CombatManager:
    """
    This class controls the flow of combat and coordinates between combatants,
    statuses, and effects.
    """
    def __init__(self, event_manager):
        """
        Initialize a new CombatManager.
        """
        self.event_manager = event_manager

    def is_combat_over(self, player, enemy) -> bool:
        """
        Check if either combatant is dead.
        """
        return not (player.is_alive() and enemy.is_alive())

    def do_combat(self, player, enemy, registries, card_cache):
        """
        Enter the combat loop.
        """
        self.event_manager.dispatch('start_combat', player, enemy)
        player.card_manager.shuffle()
        enemy.card_manager.shuffle()
        while True:
            self.do_player_turn(
                player, enemy, registries, card_cache
                )
            if self.is_combat_over(player, enemy):
                break
            self.do_enemy_turn(player, enemy, registries)
            if self.is_combat_over(player, enemy):
                break
        if player.get_health() > 0:
            player.status_manager.reset_statuses(player, registries.statuses)
            player.modifier_manager.reset_all()
            player.card_manager.reset_consumed_cards()
            self.present_rewards(
                player, enemy, card_cache, registries.effects
                )

    def do_player_turn(
            self, player, enemy, registries, card_cache
            ):
        """
        Prepare for the player to take their turn then handle any actions they
        perform.
        """
        if self.beginning_of_turn(player, enemy, registries):
            return
        turn_ended = False
        while not turn_ended and not self.is_combat_over(player, enemy):
            text_interface.display_turn_info(player, enemy, registries.effects)
            turn_ended = self.do_player_action(
                player, enemy, text_interface, registries, card_cache
                )
        self.end_of_turn(player, registries.statuses)

    def beginning_of_turn(self, combatant, opponent, registries) -> bool:
        """
        Handle resetting resources, triggering statuses, and drawing cards.
        Returns whether combat ended during the beginning phase.
        """
        combatant.reset_for_turn()

        combatant.card_manager.draw_hand(combatant, registries)

        combatant.status_manager.trigger_statuses_on_turn(
            combatant, registries.statuses
            )
        if self.is_combat_over(combatant, opponent):
            return True

        combatant.modifier_manager.recalculate_all_effects(
            registries.statuses, combatant.card_manager
            )

        combatant.replenish_resources_for_turn()
        return False

    def end_of_turn(self, combatant, status_registry):
        """
        Discard hand and decrement active status levels.
        """
        if not combatant.status_manager.has_status(
                c.StatusNames.SLOWFALLING.name, combatant, status_registry
                ):
            combatant.card_manager.discard_hand(combatant, status_registry)
        combatant.status_manager.decrement_statuses(
            combatant, status_registry
            )

    def do_player_action(self, player, enemy, registries, card_cache):
        """
        Get the player input and perform the selected action.
        """
        selection = text_interface.turn_options_prompt(
            player, enemy, registries, card_cache
            )
        if selection < 0:  # Pass turn
            return True
        if selection >= len(player.card_manager.hand):
            return False
        card = player.card_manager.hand[selection]
        if self.play_card(player, enemy, card, registries):
            player.cards_played_this_turn += 1
        return self.is_combat_over(player, enemy)

    def play_card(self, combatant, opponent, card, registries) -> bool:
        """
        Activate a card's effects, spend its cost, and discard it. Return
        whether the card was successfully played.
        """
        if not self.card_can_be_played(combatant, card, registries.statuses):
            text_interface.send_message("Impossible!")
            return False

        resource_id = card.get_resource()
        if not combatant.resources[resource_id].try_spend(card.get_cost()):
            text_interface.send_message("Not enough " + resource_id)
            return False

        for effect_id, effect_level in card.effects.items():
            if not self.effect_can_resolve(
                    combatant, effect_id, registries.statuses
                    ):
                continue
            effect = registries.effects.get_effect(effect_id)
            level = effect_level.get_level()
            effect.resolve(
                combatant, opponent, level, status_registry=registries.statuses
                )

        combatant.card_manager.discard(
            card, combatant, registries.statuses, True
            )

        text_interface.send_message(c.CARD_PLAYED_MESSAGE.format(
            combatant.name, card.name, opponent.name, opponent.get_health())
            )
        return True

    def card_can_be_played(self, combatant, card, status_registry) -> bool:
        """
        Check if the given card can be played based on current status effects
        and player class.
        """
        for status_id in combatant.status_manager.statuses:
            status = status_registry.get_status(status_id)
            if isinstance(status, RestrictCardTypeStatus):
                if not status.is_card_playable(card.card_type):
                    return False
            elif (isinstance(status, LimitCardPlayStatus) and
                  combatant.cards_played_this_turn >= status.card_limit):
                return False

        if combatant.is_enemy:
            return True

        if card.subtype in c.ALLOWED_TYPES["ALL"] or \
            card.subtype in c.ALLOWED_TYPES[combatant.character_class]:
            return True
        return False

    def effect_can_resolve(self, combatant, effect_id, status_registry) -> bool:
        """
        Check if the given card effect can resolve based on current status
        effects.
        """
        for status_id in combatant.status_manager.statuses:
            status = status_registry.get_status(status_id)
            if isinstance(status, FilterEffectStatus):
                if not status.effect_can_resolve(effect_id):
                    return False
        return True

    def do_enemy_turn(self, player, enemy, registries):
        """
        Process enemy actions.
        """
        self.beginning_of_turn(enemy, player, registries)
        playable_card_exists = True
        while playable_card_exists and not self.is_combat_over(player, enemy):
            playable_card_exists = False
            for card in enemy.card_manager.hand:
                resource_id = card.get_resource()
                if card.cost <= enemy.resources[resource_id].current and \
                    self.card_can_be_played(enemy, card, registries.statuses):
                    playable_card_exists = True
                    if self.play_card(enemy, player, card, registries):
                        enemy.cards_played_this_turn += 1
                    if self.is_combat_over(player, enemy):
                        return
                    break
        text_interface.send_message(c.ENEMY_PASSES_MESSAGE.format(enemy.name))
        self.end_of_turn(enemy, registries.statuses)

    def present_rewards(self, player, enemy, card_cache, effect_registry):
        """
        Give rewards to player.
        """
        player.gain_gold(enemy.loot.gold)
        player.gain_exp(enemy.loot.exp)
        text_interface.rewards_message(enemy.loot.gold, enemy.loot.exp)
        card_rewards = c.NORMAL_CARD_REWARD
        if enemy.loot.is_boss:
            card_rewards = c.BOSS_CARD_REWARD
        cards = enemy.loot.select_cards(
            card_rewards, player.character_class, card_cache)
        for card in cards:
            if text_interface.card_reward_prompt(card, effect_registry):
                success, too_many_copies, too_many_cards = \
                    player.card_manager.try_add_to_deck(card)
                if not success:
                    if too_many_copies:
                        text_interface.send_message(
                            c.TOO_MANY_COPIES.format(
                                c.MAX_CARD_FREQUENCY, card.name
                                )
                            )
                    if too_many_cards:
                        text_interface.send_message(
                            c.TOO_MANY_CARDS.format(c.MAX_DECK_SIZE)
                            )
