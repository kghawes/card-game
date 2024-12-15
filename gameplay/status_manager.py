class StatusManager():
    def __init__(self):
        self.statuses = dict()
    
    def has_status(self, status_id) -> bool:
        if status_id in self.statuses:
            if self.statuses[status_id] > 0:
                return True
            else:
                self.remove(status_id)
        return False
    
    def apply(self, status_id, level):
        if self.has_status(status_id):
            self.statuses[status_id] += level
        else:
            self.statuses[status_id] = level
    
    def remove(self, status_id, levels):
        if self.has_status(status_id):
            if self.statuses[status_id] > levels:
                self.statuses[status_id] -= levels
            else:
                del self.statuses[status_id]
    
    def decrement_statuses(self):
        for status in self.statuses.keys():
            self.remove(status, 1)