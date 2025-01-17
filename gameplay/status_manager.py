"""
This module defines the StatusManager class.
"""
from core.statuses import ModifyCostStatus
from utils.constants import StatusNames

class StatusManager:
    """
    This class maintains a list of active statuses and handles their
    application, removal, and activation.
    """
    def __init__(self):
        """
        Initialize a new StatusManager.
        """
        self.statuses = {}

    def _kill_zombie(self, status_id, subject, status_registry):
        """
        Remove a status with a nonpositive level.
        """
        if self.statuses.get(status_id, 1) <= 0:
            self._delete(status_id, subject, status_registry)

    def _delete(self, status_id, subject, status_registry):
        """
        Remove the status, making sure it cleans up after itself.
        """
        status_registry.get_status(status_id).expire(subject)
        del self.statuses[status_id]

    def has_status(self, status_id, subject, status_registry) -> bool:
        """
        Check if the given status is currently active.
        """
        self._kill_zombie(status_id, subject, status_registry)
        return status_id in self.statuses

    def get_status(self, status_id, subject, status_registry):
        """
        Return the Status object with the given id and its current level.
        """
        if self.has_status(status_id, subject, status_registry):
            status = status_registry.get_status(status_id)
            level = self.get_status_level(status_id)
            return status, level
        return None, 0

    def get_status_level(self, status_id) -> int:
        """
        Get the current level of the status if active, or else 0.
        """
        return self.statuses.get(status_id, 0)

    def change_status(
            self, status_id, amount, subject, status_registry,
            remove_all_levels=False
            ):
        """
        Change the level of the status with the given id.
        """
        current_level = self.get_status_level(status_id)
        new_level = max(current_level + amount, 0)

        if remove_all_levels and status_id in self.statuses:
            self._delete(status_id, subject, status_registry)
        else:
            self.statuses[status_id] = new_level
        self._kill_zombie(status_id, subject, status_registry)

        # Handle consequences of statuses being changed or removed
        status = status_registry.get_status(status_id)
        if status.applies_immediately:
            status.trigger_on_change(subject, new_level - current_level)

        if status_id not in self.statuses:
            subject.modifier_manager.clear_effect_modifiers(
                status, subject.card_manager
                )
        subject.modifier_manager.recalculate_all_effects(
            status_registry, subject.card_manager
            )

        levitate_id = StatusNames.LEVITATE.name
        if isinstance(status, ModifyCostStatus) \
        and self.has_status(levitate_id, subject, status_registry):
            levitate = status_registry.get_status(levitate_id)
            levitate_level = self.get_status_level(levitate_id)
            levitate.trigger_on_change(subject, levitate_level)
        elif status_id == levitate_id:
            subject.modifier_manager.recalculate_all_costs(
                status_registry, subject.card_manager
                )

    def change_all_statuses(self, amount, subject, status_registry):
        """
        Change the level of every active status by the same amount.
        """
        for status_id in list(self.statuses.keys()):
            self.change_status(status_id, amount, subject, status_registry)

    def decrement_statuses(self, subject, status_registry):
        """
        Reduce the level of every active status by 1.
        """
        self.change_all_statuses(-1, subject, status_registry)

    def reset_statuses(self, subject, status_registry):
        """
        Remove all active statuses.
        """
        while len(self.statuses) > 0:
            status_id = next(iter(self.statuses))
            self._delete(status_id, subject, status_registry)

    def trigger_statuses_on_turn(self, subject, status_registry):
        """
        Loop over active statuses and invite them to trigger their on-turn
        effects.
        """
        for status_id, level in self.statuses.items():
            status = status_registry.get_status(status_id)
            status.trigger_on_turn(subject, level, status_registry)
            if not subject.is_alive():
                return
        # Trigger recalculations after statuses resolve
        subject.modifier_manager.recalculate_all_effects(
            status_registry, subject.card_manager
            )
        return
