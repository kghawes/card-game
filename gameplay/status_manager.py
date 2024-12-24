class StatusManager:

    def __init__(self):
        self.statuses = {}
        
    def _kill_zombie(self, status_id):
        if self.statuses.get(status_id, 1) <= 0:
            del self.statuses[status_id]

    def has_status(self, status_id) -> bool:
        self._kill_zombie(status_id)
        return status_id in self.statuses
    
    def get_status_level(self, status_id) -> int:
        return self.statuses.get(status_id, 0)
    
    def change_status(self, status_id, level, remove_all_levels=False):
        if remove_all_levels and status_id in self.statuses:
            del self.statuses[status_id]
        else:
            self.statuses[status_id] = self.statuses.get(status_id, 0) + level
        self._kill_zombie(status_id)

    def decrement_statuses(self):
        for status_id in list(self.statuses.keys()):
            self.change_status(status_id, -1)
    
    def remove_all_statuses(self):
        self.statuses.clear()

    def trigger_statuses_on_turn(self, subject, status_registry):
        for status_id, level in self.statuses.items():
            status = status_registry.get_status(status_id)
            status.trigger_on_turn(subject, level)
            if not subject.is_alive():
                return
        return
