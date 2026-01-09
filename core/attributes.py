from utils.utils import load_json

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
        self.card_type_index = self.setup_card_type_index()

    def setup_card_type_index(self) -> dict:
        """
        Setup index for quick lookup of attributes by card type.
        Assumes max one attribute per card type.
        """
        card_types = {}
        for attr_name, attr_data in self.attributes.items():
            attr_type = attr_data.get("card_type", None)
            if attr_type:
                card_types[attr_type] = attr_name
        return card_types
    
    def get_attribute_description(self, name) -> str:
        """
        Get the description of a specific attribute.
        """
        return self.attributes.get(name, {}).get("description", "")

    def get_attribute_modifiers(self, name) -> dict:
        """
        Get the modifier map associated with a specific attribute.
        """
        return self.attributes.get(name, {}).get("modifiers", {})

    def _get_modifier_for_subtypes(self, modifiers, subtypes):
        """
        Get the matching modifier value for the provided subtypes.
        """
        if not modifiers:
            return None
        for subtype in subtypes or []:
            if subtype in modifiers:
                return modifiers[subtype]
        if "ALL" in modifiers:
            return modifiers["ALL"]
        return None

    def get_attribute_modifier(self, name, subtypes) -> float:
        """
        Get the modifier value associated with a specific attribute and subtypes.
        """
        modifier = self._get_modifier_for_subtypes(
            self.get_attribute_modifiers(name),
            subtypes,
        )
        return 0 if modifier is None else modifier
    
    def get_attribute_affected_effect(self, name) -> str:
        """
        Get the string ID of the effect that is affected by a specific attribute.
        """
        return self.attributes.get(name, {}).get("affected_effect", "")
    
    def get_starting_attributes(self, char_class) -> dict:
        """
        Get the starting attributes for a given character class.
        """
        return self.starting_attributes.get(char_class, {})

    def get_attribute_by_context(self, card_type, subtypes, effect_id=None):
        """
        Get the relevant attribute and modifier for a given card type, subtypes,
        and effect.
        """
        attr_name = self.card_type_index.get(card_type, None)
        # If no attribute affects this card type, return None
        if not attr_name:
            return None
        # If effect_id and affected_effect are specified,
        # ensure the effect matches the attribute's affected effect
        affected_effect = self.get_attribute_affected_effect(attr_name)
        if effect_id and affected_effect and affected_effect not in effect_id:
            return None
        # Check if the subtypes match the attribute's modifiers
        modifiers = self.get_attribute_modifiers(attr_name)
        modifier_value = self._get_modifier_for_subtypes(modifiers, subtypes)
        if modifier_value is not None:
            return attr_name, modifier_value
        return None
