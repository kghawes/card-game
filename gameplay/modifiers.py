import utils.constants as constants

class Modifier:
    def __init__(self, modifier_id):
        self.modifier_id = modifier_id
    
    def modify_value(self, level, value) -> int:
        return value

class ScalingModifier(Modifier):
    def __init__(self, modifier_id, is_buff=False, minimum_result=0):
        super().__init__(modifier_id)
        self.multiplier = constants.SCALING_BUFF_MULTIPLIER if is_buff else constants.SCALING_DEBUFF_MULTIPLIER
        self.minimum_result = minimum_result
    
    def modify_value(self, level, value) -> float:
        return self.multiplier ** level * value

class FlatModifier(Modifier):
    def __init__(self, modifier_id, is_adding=False, minimum_result=0):
        super().__init__(modifier_id)
        self.is_adding = is_adding
        self.minimum_result = minimum_result
    
    def modify_value(self, level, old_value) -> int:
        if self.is_adding:
            return old_value + level
        else:
            return max(old_value - level, self.minimum_result)