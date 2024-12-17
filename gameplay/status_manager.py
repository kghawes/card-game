class StatusManager:
    REMOVE_ALL = None

    def __init__(self):
        self.statuses = {}

    def has_status(self, status_id) -> bool:
        self._kill_zombie(status_id)
        return status_id in self.statuses

    def apply(self, status_id, level):
        if level > 0:
            self.statuses[status_id] = self.statuses.get(status_id, 0) + level
        else:
            self._kill_zombie(status_id)

    def remove(self, status_id, levels_to_remove=REMOVE_ALL):
        if status_id in self.statuses:
            if levels_to_remove is self.REMOVE_ALL or self.statuses[status_id] <= levels_to_remove:
                del self.statuses[status_id]
            else:
                self.statuses[status_id] -= levels_to_remove
        self._kill_zombie(status_id)
        
    def _kill_zombie(self, status_id):
        if status_id in self.statuses and self.statuses[status_id] <= 0:
            del self.statuses[status_id]
    
    def change_status(self, status_id, level):
        if level > 0:
            self.apply(status_id, level)
        elif level < 0:
            self.remove(status_id, abs(level))

    def decrement_statuses(self):
        for status_id in list(self.statuses.keys()):
            self.remove(status_id, 1)

    def trigger_statuses(self, subject, status_registry):
        for status_id, level in self.statuses.items():
            status = status_registry.get_status(status_id)
            status.trigger_on_turn(subject, level)
            if not subject.is_alive():
                return
        return
