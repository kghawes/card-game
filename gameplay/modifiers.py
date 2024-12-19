class Modifier:
    def __init__(self, modifier_id):
        self.modifier_id = modifier_id
    
    def modify_value(self, level, value) -> int:
        return value

class ScalingModifier(Modifier):
    def __init__(self, modifier_id, scale_factor, base_multiplier=1):
        super().__init__(modifier_id)
        self.m = scale_factor
        self.b = base_multiplier
    
    def modify_value(self, level, value) -> int:
        multiplier = self.m * level + self.b
        return round(multiplier * value)

class FlatModifier(Modifier):
    def __init__(self, modifier_id, is_adding, minimum_result=0):
        super().__init__(modifier_id)
        self.is_adding = is_adding
        self.minimum_result = minimum_result
    
    def modify_value(self, level, value) -> int:
        if self.is_adding:
            return value + level
        else:
            return max(value - level, self.minimum_result)