"""
This module defines the StatusManager class.
"""
from core.statuses import ModifyCostStatus
from core.leveled_mechanics import LeveledMechanic
from utils.constants import StatusNames

class StatusManager:
    """
    This class maintains a list of active statuses and handles their
    application, removal, and activation.
    """
    def __init__(self, event_manager):
        """
        Initialize a new StatusManager.
        """
        self.statuses = {}
        self.event_manager = event_manager

    def _delete(self, status_id, subject):
        """
        Remove the status, making sure it cleans up after itself.
        """
        if status_id not in self.statuses:
            return
        leveled_status = self.statuses[status_id]
        leveled_status.reference.expire(subject, self.event_manager.logger)
        del self.statuses[status_id]

    def get_leveled_status(self, status_id) -> LeveledMechanic:
        """
        Return the LeveledMechanic object representing the status and its level.
        Return None if the status is not active.
        """
        if status_id in self.statuses:
            return self.statuses[status_id]
        return None

    def change_status(
            self, status_id, amount, subject, status_registry,
            remove_all_levels=False
            ):
        """
        Change the level of the status with the given id.
        """
        if amount == 0:
            return
        
        # Get the leveled status or create a new one if it doesn't exist
        leveled_status = self.get_leveled_status(status_id)
        if leveled_status is None:
            status = status_registry.get_status(status_id)
            if status is None:
                return
            leveled_status = LeveledMechanic(status, 0)

        current_level = leveled_status.get_level()
        new_level = max(current_level + amount, 0)
        change = new_level - current_level

        if leveled_status.get_level() > 0:
            if remove_all_levels or new_level == 0:
                self._delete(status_id, subject)
            else:
                leveled_status.change_level(change)
        elif new_level > 0:
            self.statuses[status_id] = leveled_status

        # Handle consequences of statuses being changed or removed
        if status.applies_immediately:
            status.trigger_on_change(subject, change)

        if status_id not in self.statuses:
            subject.modifier_manager.clear_effect_modifiers(
                status, subject.card_manager
                )
            
        subject.modifier_manager.recalculate_all_effects(
            status_registry, subject.card_manager
            )

        levitate_id = StatusNames.LEVITATE.name
        if isinstance(status, ModifyCostStatus) and levitate_id in self.statuses:
            # If the status is a cost modifier and levitate is active, trigger recalculation
            levitate = self.get_leveled_status(levitate_id)
            levitate_level = levitate.get_level()
            levitate.reference.trigger_on_change(subject, levitate_level)
        elif status_id == levitate_id:
            subject.modifier_manager.recalculate_all_costs(
                status_registry, subject.card_manager
                )

    def change_all_statuses(self, amount, subject, status_registry):
        """
        Change the level of every active status by the same amount.
        """
        for status_id in self.statuses.copy():
            self.change_status(status_id, amount, subject, status_registry)

    def decrement_statuses(self, subject, status_registry):
        """
        Reduce the level of every active status by 1.
        """
        self.change_all_statuses(-1, subject, status_registry)

    def reset_statuses(self, subject):
        """
        Remove all active statuses.
        """
        while len(self.statuses) > 0:
            status_id = next(iter(self.statuses))
            self._delete(status_id, subject)

    def trigger_statuses_on_turn(self, subject, status_registry):
        """
        Loop over active statuses and invite them to trigger their on-turn
        effects.
        """
        for leveled_status in self.statuses.values():
            status = leveled_status.reference
            level = leveled_status.get_level()
            status.trigger_on_turn(subject, level, status_registry)
            if not subject.is_alive():
                return
        # Trigger recalculations after statuses resolve
        subject.modifier_manager.recalculate_all_effects(
            status_registry, subject.card_manager
            )
