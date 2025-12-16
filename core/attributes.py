from math import floor
from utils.utils import load_json
from utils.constants import WeightClasses, Attributes, MIN_COST, MIN_EFFECT, \
    MIN_HAND_SIZE, HAND_SIZE, MAX_HAND_SIZE, MERCHANT_PENALTY

class AttributeRegistry:
    """
    Registry for character attributes.
    """
    def __init__(self, attributes_path):
        """
        Initialize the attribute registry by loading data from JSON.
        """
        data = load_json(attributes_path)
        self.attributes = data["ATTRIBUTES"]
        self.starting_attributes = data["STARTING_ATTRIBUTES"]
        self.modifiers = self.setup_modifiers()
    
    def setup_modifiers(self) -> dict:
        """
        Setup attribute modifiers for quick lookup.
        """
        modifiers = {}
        for attr_name, attr_data in self.attributes.items():
            modifiers[attr_name] = attr_data.get("modifiers", {})
        return modifiers
    
    def get_attribute_description(self, name):
        """
        Get the description of a specific attribute.
        """
        return self.attributes.get(name, {}).get("description", "")
    
    def get_attribute_modifiers(self, name):
        """
        Get the modifiers associated with a specific attribute.
        """
        return self.attributes.get(name, {}).get("modifiers", {})
    
    def get_starting_attributes(self, char_class):
        """
        Get the starting attributes for a given character class.
        """
        return self.starting_attributes.get(char_class, {})
    
    def _calculate_effect_bonus(self, attr_name, attr_value, base_value, modifier_class) -> int:
        """
        General method to calculate effect bonus based on attribute.
        """
        if attr_value * base_value == 0 or modifier_class not in WeightClasses:
            return base_value
        base_modifier = self.modifiers[attr_name].get(modifier_class, 0)
        leveled_modifier = base_modifier * attr_value
        modified_value = base_value * (1 + leveled_modifier)
        return max(MIN_EFFECT, floor(modified_value))
    
    def _calculate_reduction_bonus(self, attr_name, attr_value, base_value, minimum) -> int:
        """
        General method to calculate simple reduction based on attribute.
        """
        if attr_value * base_value == 0:
            return base_value
        base_modifier = self.modifiers[attr_name].get("ALL", 0)
        leveled_modifier = base_modifier * attr_value
        reduced_value = base_value * (1 - leveled_modifier)
        return max(minimum, floor(reduced_value))
    
    def calculate_strength_bonus(self, str_value, weapon_weight, base_damage) -> int:
        """
        Calculate net physical damage from Strength attribute.
        """
        return self._calculate_effect_bonus(
            Attributes.STRENGTH.name, str_value, base_damage, weapon_weight
            )
    
    def calculate_endurance_bonus(self, end_value, armor_weight, base_defense) -> int:
        """
        Calculate net defense from Endurance attribute.
        """
        return self._calculate_effect_bonus(
            Attributes.ENDURANCE.name, end_value, base_defense, armor_weight
            )

    def calculate_agility_bonus(self, agi_value, base_cost) -> int:
        """
        Calculate stamina cost reduction from Agility attribute.
        """
        return self._calculate_reduction_bonus(
            Attributes.AGILITY.name, agi_value, base_cost, MIN_COST
            )
    
    def calculate_speed_bonus(self, spd_value) -> int:
        """
        Calculate card draw from Speed attribute.
        """
        base_modifier = self.modifiers[Attributes.SPEED.name].get("ALL", 0)
        hand_size = HAND_SIZE + base_modifier * spd_value
        return min(MAX_HAND_SIZE, max(MIN_HAND_SIZE, floor(hand_size)))
    
    def calculate_intelligence_bonus(self, int_value, base_cost) -> int:
        """
        Calculate magicka cost reduction from Intelligence attribute.
        """
        return self._calculate_reduction_bonus(
            Attributes.INTELLIGENCE.name, int_value, base_cost, MIN_COST
            )
    
    def calculate_willpower_bonus(self, wil_value, base_damage) -> int:
        """
        Calculate net incoming magic damage from Willpower attribute.
        """
        return self._calculate_reduction_bonus(
            Attributes.WILLPOWER.name, wil_value, base_damage, MIN_EFFECT
            )
    
    def calculate_personality_bonus(self, per_value) -> int:
        """
        Calculate net merchant penalty from Personality attribute.
        """
        base_modifier = self.modifiers[Attributes.PERSONALITY.name].get("ALL", 0)
        return MERCHANT_PENALTY - (base_modifier * per_value)
    
    def calculate_luck_bonus(self, luck_value, base_chance) -> int:
        """
        Calculate modified probability from Luck attribute.
        """
        if luck_value == 0 or base_chance == 0:
            return base_chance
        base_modifier = self.modifiers[Attributes.LUCK.name].get("ALL", 0)
        leveled_modifier = base_modifier * luck_value
        modified_chance = base_chance + leveled_modifier
        return min(1, max(0, modified_chance))