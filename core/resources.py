"""
This module defines the Resource class.
"""
from utils.constants import MIN_RESOURCE

class Resource:
    """Represents health, stamina, or magicka."""
    def __init__(self, resource_id, max_value):
        """Initialize a new Resource."""
        self.resource_id = resource_id
        self.max_value = max_value
        self.current = max_value

    def clamp_value(self, value, modifier_manager) -> int:
        """Restrict the value to within the bounds set by the minimum
        and maximum."""
        value = max(value, MIN_RESOURCE)
        return min(value, self.get_max(modifier_manager))

    def change_value(self, amount, modifier_manager):
        """Change the current value by the given amount."""
        new_value = self.current + amount
        new_value = self.clamp_value(new_value, modifier_manager)
        self.current = new_value

    def try_spend(self, amount) -> bool:
        """Reduce the current value by the given amount or return false
        if there isn't enough."""
        if self.current < amount:
            return False
        self.current = self.current - amount
        return True

    def get_max(self, modifier_manager) -> int:
        """Get the current maximum value."""
        return modifier_manager.get_max_resource(
            self.resource_id, self.max_value
            )

    def replenish(self, modifier_manager):
        """Reset the current value to the maximum value."""
        self.current = self.get_max(modifier_manager)
