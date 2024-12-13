from utils import Prototype

class Card:
    def __init__(self, name, damage, cost):
        self.name = name
        self.damage = damage
        self.cost = cost

    def __repr__(self):
        return f"Card(name={self.name}, damage={self.damage}, cost={self.cost})"

class CardPrototype(Card, Prototype):
    required_fields = ["name", "damage", "cost"]

    def clone(self):
        return Card(self.name, self.damage, self.cost)

class CardCache:
    def __init__(self, filename):
        self.card_prototypes = CardPrototype.load_prototypes(
            filename=filename,
            required_fields=CardPrototype.required_fields,
            prototype_class=CardPrototype
        )

    def create_card(self, card_id: str) -> Card:
        if card_id not in self.card_prototypes:
            raise KeyError(f"Card ID '{card_id}' not found.")
        return self.card_prototypes[card_id].clone()

    def list_cards(self):
        return list(self.card_prototypes.keys())
