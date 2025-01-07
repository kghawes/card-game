"""
This module contains prototyping and JSON loading logic.
"""
import json
import sys
from abc import ABC, abstractmethod

def load_json(filepath: str):
    """Load data from the JSON file."""
    try:
        with open(filepath, "r") as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading JSON file {filepath}:")
        sys.exit(e)

class Prototype(ABC):
    """Prototype class for creating many instances from a template."""
    @abstractmethod
    def clone(self):
        """Create an object based on the prototype."""
        pass

    def load_prototypes(filename, required_fields, prototype_class) -> dict:
        """Turn the data in a JSON file into a collection of prototypes."""
        data = load_json(filename)

        prototypes = {}
        for prototype_id, attributes in data.items():
            if not all(key in attributes for key in required_fields):
                raise ValueError(
                    f"Prototype '{prototype_id}' is missing required fields: {required_fields}"
                )

            prototypes[prototype_id] = prototype_class(**attributes)

        return prototypes
