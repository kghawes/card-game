from abc import ABC, abstractmethod
from utils.constants import StatusNames, DamageTypes

class Status(ABC):
    def __init__(self, status_id, name):
        self.status_id = status_id
        self.name = name
    
    @abstractmethod
    def trigger_on_turn(self, subject, level, *args, **kwargs) -> bool:
        """Triggers the status effect for the subject. Returns whether it ends combat."""
        pass

class DefenseStatus(Status):
    def __init__(self):
        super().__init__(StatusNames.DEFENSE.name, StatusNames.DEFENSE.value)
    
    def trigger_on_turn(self, subject, level, *args, **kwargs) -> bool:
        # Defense doesn't trigger any combat-ending effect
        return False

class PoisonStatus(Status):
    def __init__(self):
        super().__init__(StatusNames.POISON.name, StatusNames.POISON.value)
    
    def trigger_on_turn(self, subject, level, *args, **kwargs) -> bool:
        # Poison deals damage based on its level
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