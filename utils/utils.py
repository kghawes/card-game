import json
from abc import ABC, abstractmethod

def load_json(filepath: str):
    with open(filepath, "r") as file:
        return json.load(file)

class Prototype(ABC):
    @abstractmethod
    def clone(self):
        pass

    def load_prototypes(filename, required_fields, prototype_class) -> dict:
        data = load_json(filename)
        
        prototypes = {}
        for prototype_id, attributes in data.items():
            if not all(key in attributes for key in required_fields):
                raise ValueError(
                    f"Prototype '{prototype_id}' is missing required fields: {required_fields}"
                )
            
            prototypes[prototype_id] = prototype_class(**attributes)
        
        return prototypes