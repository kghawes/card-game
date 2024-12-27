class StatusManager:

    def __init__(self):
        self.statuses = {}

    def _kill_zombie(self, status_id, subject, status_registry):
        if self.statuses.get(status_id, 1) <= 0:
            self._delete(status_id, subject, status_registry)

    def _delete(self, status_id, subject, status_registry):
        status_registry.get_status(status_id).expire(subject)
        del self.statuses[status_id]

    def has_status(self, status_id, subject, status_registry) -> bool:
        self._kill_zombie(status_id, subject, status_registry)
        return status_id in self.statuses

    def get_status(self, status_id, subject, status_registry):
        if self.has_status(status_id, subject, status_registry):
            status = status_registry.get_status(status_id)
            level = self.get_status_level(status_id)
            return status, level
        else:
            return None, 0

    def get_status_level(self, status_id) -> int:
        return self.statuses.get(status_id, 0)

    def change_status(self, status_id, level, subject, status_registry, remove_all_levels=False):
        if remove_all_levels and status_id in self.statuses:
            self._delete(status_id, subject, status_registry)
        else:
            self.statuses[status_id] = self.statuses.get(status_id, 0) + level
        self._kill_zombie(status_id, subject, status_registry)

        if self.has_status(status_id, subject, status_registry):
            status = status_registry.get_status(status_id)
            if status.applies_immediately:
                status.trigger_on_change(subject, level)

    def decrement_statuses(self, subject, status_registry):
        for status_id in list(self.statuses.keys()):
            self.change_status(status_id, -1, subject, status_registry)

    def reset_statuses(self):
        self.statuses.clear()

    def trigger_statuses_on_turn(self, subject, status_registry):
        for status_id, level in self.statuses.items():
            status = status_registry.get_status(status_id)
            status.trigger_on_turn(subject, level, status_registry)
            if not subject.is_alive():
                return
        # Trigger recalculations after statuses resolve
        subject.recalculate_all_modifiers()
        return
