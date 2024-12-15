class StatusManager:
    REMOVE_ALL = None

    def __init__(self):
        self.statuses = {}

    def has_status(self, status_id) -> bool:
        return status_id in self.statuses and self.statuses[status_id] > 0

    def apply(self, status_id, level):
        self.statuses[status_id] = self.statuses.get(status_id, 0) + level

    def remove(self, status_id, levels_to_remove=REMOVE_ALL):
        if status_id in self.statuses:
            if levels_to_remove is self.REMOVE_ALL or self.statuses[status_id] <= levels_to_remove:
                del self.statuses[status_id]
            else:
                self.statuses[status_id] -= levels_to_remove

    def decrement_statuses(self):
        for status_id in list(self.statuses.keys()):
            self.remove(status_id, 1)

    def trigger_statuses(self, status_registry, subject, *args, **kwargs) -> bool:
        for status_id, level in self.statuses.items():
            status = status_registry.get_status(status_id)
            if status.trigger_on_turn(subject, level, *args, **kwargs):
                return True
        return False
