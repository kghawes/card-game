from copy import copy
from utils.utils import Prototype

class Card:
    def __init__(self, name, card_type, cost, value, effects):
        self.name = name
        self.card_type = card_type
        self.cost = cost
        self.value = value
        self.effects = copy(effects)

class CardPrototype(Card, Prototype):
    required_fields = ["name", "card_type", "cost", "value", "effects"]

    def clone(self):
        return Card(self.name, self.card_type, self.cost, self.value, self.effects)

class CardCache:
    def __init__(self, filenames):
        self.card_prototypes = {}
        for filename in filenames:
            self._load_prototypes_from_file(filename)

    def _load_prototypes_from_file(self, filename):
        prototypes = CardPrototype.load_prototypes(
            filename=filename,
            required_fields=CardPrototype.required_fields,
            prototype_class=CardPrototype
        )
        for card_id, prototype in prototypes.items():
            if card_id in self.card_prototypes:
                raise ValueError(f"Duplicate card ID '{card_id}' found in file '{filename}'.")
            self.card_prototypes[card_id] = prototype

    def create_card(self, card_id: str) -> Card:
        if card_id not in self.card_prototypes:
            raise KeyError(f"Card ID '{card_id}' not found.")
        return self.card_prototypes[card_id].clone()

    def list_cards(self):
        return list(self.card_prototypes.keys())
