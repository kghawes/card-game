from utils.constants import StatusNames, DamageTypes

class Status:
    def __init__(self, status_id, name):
        self.status_id = status_id
        self.name = name
    
    def trigger_on_turn(self, subject, level) -> bool: # returns whether the status effect ended combat
        return False

class DefenseStatus(Status):
    def __init__(self):
        super().__init__(StatusNames.DEFENSE.name, StatusNames.DEFENSE.value)
    
    def trigger_instantly(self, subject, level, incoming_damage, damage_type) -> bool:
        if not subject.take_damage(incoming_damage - level, damage_type):
            return True
        subject.status_manager.remove(self.status_id, incoming_damage)
        return False

class PoisonStatus(Status):
    def __init__(self):
        super().__init__(StatusNames.POISON.name, StatusNames.POISON.value)
    
    def trigger_on_turn(self, subject, level) -> bool:
        return subject.take_damage(level, DamageTypes.POISON)

class StatusRegistry:
    def __init__(self):
        self.statuses = self._initialize_statuses()
    
    def _initialize_statuses(self) -> dict:
        defense_status = DefenseStatus()
        poison_status = PoisonStatus()
        
        return {
            defense_status.status_id: defense_status,
            poison_status.status_id: poison_status
        }
    
    def get_status(self, status_id) -> Status:
        if status_id not in self.statuses:
            raise KeyError(f"Status ID '{status_id}' not found.")
        return self.statuses[status_id]