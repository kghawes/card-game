import json

class Card:
    def __init__(self, name: str, damage: int, cost: int):
        self.name = name
        self.damage = damage
        self.cost = cost

def load_cards(filename: str):
    with open(filename, "r") as file:
        data = json.load(file)
    cards = {}
    for card_id, card_data in data.items():
        if not all(k in card_data for k in ("name", "damage", "cost")):
            raise ValueError(f"Card {card_id} is missing required fields.")
        cards[card_id] = Card(
            name=card_data["name"],
            damage=card_data["damage"],
            cost=card_data["cost"]
        )
    return cards