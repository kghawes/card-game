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

    def start_combat(self, player, enemy):
        """
        Set up for combat.
        """
        player.card_manager.shuffle()
        enemy.card_manager.shuffle()
        self.event_manager.dispatch('start_combat', enemy)

    def beginning_of_turn(self, combatant, opponent, registries):
        """
        Handle resetting resources, triggering statuses, and drawing cards.
        """
        combatant.reset_for_turn()
        combatant.card_manager.draw_hand(combatant, registries)
        combatant.status_manager.trigger_statuses_on_turn(
            combatant, registries.statuses
            )
        if self.is_combat_over(combatant, opponent):
            self.event_manager.dispatch('end_combat')
        # combatant.modifier_manager.recalculate_all_effects(
        #     registries.statuses, combatant.card_manager
        #     )
        combatant.replenish_resources_for_turn()
        if not combatant.is_enemy:
            self.event_manager.dispatch('start_action_phase', combatant.card_manager.hand)

    def end_of_turn(self, combatant, status_registry):
        """
        Discard hand and decrement active status levels.
        """
        if c.StatusNames.SLOWFALLING.name not in combatant.status_manager.statuses:
            combatant.card_manager.discard_hand(combatant)
        decrement_message = ""
        if combatant.status_manager.statuses:
            decrement_message = " Active statuses decremented."
        self.event_manager.logger.log(
            f"{combatant.name} ended their turn.{decrement_message}"
            )
        combatant.status_manager.decrement_statuses(
            combatant, status_registry
            )

    def play_card(self, combatant, opponent, card, registries):
        """
        Activate a card's effects, spend its cost, and discard it.
        """
        if not self.card_can_be_played(combatant, card) \
        or not combatant.resources[card.get_resource()].try_spend(
            card.get_cost(), combatant.modifier_manager
        ):
            # TODO make card_can_be_played return a reason
            self.event_manager.logger.log(f"This {card.name} can't be played.")
            self.event_manager.dispatch('card_not_playable')
            return            

        self.event_manager.logger.log(
            f"{combatant.name} played {card.name}."
            )

        for effect in card.effects:
            if not self.effect_can_resolve(combatant, effect.str_id):
                # TODO give a reason why the effect can't resolve
                self.event_manager.logger.log(f"{effect.name} has no effect.")
                continue
            level = effect.get_level()
            effect.reference.resolve(
                combatant, opponent, level, status_registry=registries.statuses
                )
            self.event_manager.logger.log(
                f"{card.name} resolved {effect.name} at level {level}.", True
                )
            if self.is_combat_over(combatant, opponent):
                self.event_manager.dispatch('end_combat')
                return

        combatant.card_manager.discard(card, combatant, True)

        combatant.cards_played_this_turn += 1
        if not combatant.is_enemy:
            self.event_manager.dispatch('card_resolved')

    def card_can_be_played(self, combatant, card) -> bool:
        """
        Check if the given card can be played based on current status effects
        and player class.
        """
        for leveled_status in combatant.status_manager.statuses.values():
            status = leveled_status.reference
            if isinstance(status, RestrictCardTypeStatus):
                if not status.is_card_playable(card.card_type):
                    return False
            elif (isinstance(status, LimitCardPlayStatus) and
                  combatant.cards_played_this_turn >= status.card_limit):
                return False
        return True
        # if combatant.is_enemy:
        #     return True

        # if any(subtype in c.ALLOWED_TYPES["ALL"] for subtype in card.subtypes) or \
        #    any(subtype in c.ALLOWED_TYPES[combatant.character_class] for subtype in card.subtypes):
        #     return True
        # return False

    def effect_can_resolve(self, combatant, effect_id) -> bool:
        """
        Check if the given card effect can resolve based on current status effects.
        """
        for leveled_status in combatant.status_manager.statuses.values():
            status = leveled_status.reference
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
                if card.get_cost() <= enemy.resources[resource_id].current and \
                    self.card_can_be_played(enemy, card):
                    playable_card_exists = True
                    self.play_card(enemy, player, card, registries)
                    if self.is_combat_over(player, enemy):
                        return
                    break
        self.end_of_turn(enemy, registries.statuses)
        self.event_manager.dispatch('end_enemy_turn')
