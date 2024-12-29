"""
This module defines the StatusManager class.
"""

class StatusManager:
    """This class maintains a list of active statuses and handles their
    application, removal, and activation."""
    def __init__(self):
        """Initialize a new StatusManager."""
        self.statuses = {}

    def _kill_zombie(self, status_id, subject, status_registry):
        """Remove a status with a nonpositive level."""
        if self.statuses.get(status_id, 1) <= 0:
            self._delete(status_id, subject, status_registry)

    def _delete(self, status_id, subject, status_registry):
        """Remove the status, making sure it cleans up after itself."""
        status_registry.get_status(status_id).expire(subject)
        del self.statuses[status_id]

    def has_status(self, status_id, subject, status_registry) -> bool:
        """Check if the given status is currently active."""
        self._kill_zombie(status_id, subject, status_registry)
        return status_id in self.statuses

    def get_status(self, status_id, subject, status_registry):
        """Return the Status object with the given id and its current
        level."""
        if self.has_status(status_id, subject, status_registry):
            status = status_registry.get_status(status_id)
            level = self.get_status_level(status_id)
            return status, level
        return None, 0

    def get_status_level(self, status_id) -> int:
        """Get the current level of the status if active, or else 0."""
        return self.statuses.get(status_id, 0)

    def change_status(
            self, status_id, amount, subject, status_registry,
            remove_all_levels=False
            ):
        """Change the level of the status with the given id."""
        current_level = self.get_status_level(status_id)
        new_level = max(current_level + amount, 0)

        if remove_all_levels and status_id in self.statuses:
            self._delete(status_id, subject, status_registry)
        else:
            self.statuses[status_id] = new_level
        self._kill_zombie(status_id, subject, status_registry)

        status = status_registry.get_status(status_id)
        if status.applies_immediately:
            status.trigger_on_change(subject, new_level - current_level)

        if status_id not in self.statuses:
            subject.clear_effect_modifiers(status)
        subject.modifier_manager.recalculate_all_effects(status_registry)

    def decrement_statuses(self, subject, status_registry):
        """Reduce the level of every active status by 1."""
        for status_id in list(self.statuses.keys()):
            self.change_status(status_id, -1, subject, status_registry)

    def reset_statuses(self):
        """Remove all active statuses without cleaning up."""
        self.statuses.clear()

    def trigger_statuses_on_turn(self, subject, status_registry):
        """Loop over active statuses and invite them to trigger their
        start-of-turn effects."""
        for status_id, level in self.statuses.items():
            status = status_registry.get_status(status_id)
            status.trigger_on_turn(subject, level, status_registry)
            if not subject.is_alive():
                return
        # Trigger recalculations after statuses resolve
        subject.modifier_manager.recalculate_all_effects(status_registry)
        return
