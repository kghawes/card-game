"""
This module defines the Resource class and manages stats during game.
"""
import utils.constants as c

class Resource:
    """Represents health, stamina, or magicka."""
    def __init__(self, resource_enum, max_value, modifying_statuses):
        """Initialize a new Resource."""
        self.resource_enum = resource_enum
        self.max_value = max_value
        self.current_value = max_value
        self.modifier_contributions = {}
        for status_id in modifying_statuses:
            self.modifier_contributions[status_id] = 0

    def change_value(self, amount):
        """Change the current value by the given amount."""
        new_value = self.current_value + amount
        new_value = min(max(new_value, 0), self.get_max_value())
        self.current_value = new_value

    def try_spend(self, amount) -> bool:
        """Reduce the current value by the given amount or return false
        if there isn't enough."""
        if self.current_value < amount:
            return False
        self.current_value = self.current_value - amount
        return True

    def reset_max_value(self): # ?
        """Clear all modifiers and reset maximum value to its base value."""
        for status_id in self.modifier_contributions:
            self.modifier_contributions[status_id] = 0

    def clear_contribution(self, status_id):
        """Remove max value modifier contribution from a specific
        status."""
        if status_id in self.modifier_contributions:
            self.modifier_contributions[status_id] = 0

    def get_max_value(self) -> int:
        """Get the maximum value of the resource."""
        net_contribution = 0
        for contribution in self.modifier_contributions.values():
            net_contribution += contribution
        return max(self.max_value + net_contribution, c.MIN_RESOURCE)

    def modify_max_value(self, status_id, amount):
        """Change the maximum value by the given amount."""
        if status_id in self.modifier_contributions:
            old_value = self.modifier_contributions[status_id]
            new_value = old_value + amount
            self.modifier_contributions[status_id] = new_value
            self.change_value(amount)

    def replenish(self):
        """Reset the current value to the maximum value."""
        self.current_value = self.get_max_value()
