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