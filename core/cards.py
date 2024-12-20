from copy import deepcopy
from utils.utils import Prototype
from utils.constants import CardTypes, CardSubtypes

class Card:
    def __init__(self, name, card_type, cost, value, effects, subtype=None):
        self.name = name
        self.card_type = card_type
        self.cost = cost
        self.modified_cost = cost
        self.value = value
        self.effects = deepcopy(effects)
        self.subtype = subtype
        
    def get_cost(self):
        return self.modified_cost
    
    def set_cost(self, new_cost):
        self.modified_cost = new_cost
        
    def has_property(self, card_property) -> bool:
        if card_property in CardTypes:
            return self.card_type == card_property.name
        elif card_property in CardSubtypes:
            return self.subtype == card_property.name
        else:
            return False

class CardPrototype(Card, Prototype):
    def __init__(self, name, card_type, cost, value, effects, enchantments = None, enchanted_name = None):
        super().__init__(name, card_type, cost, value, effects)
        self.enchantments = enchantments
        self.enchanted_name = enchanted_name
        
    required_fields = ["name", "card_type", "cost", "value", "effects"]

    def clone(self):
        return Card(self.name, self.card_type, self.cost, self.value, self.effects)

class CardCache:
    def __init__(self, filenames, registries):
        self.card_prototypes = {}
        for filename in filenames:
            self._load_prototypes_from_file(filename, registries)

    def _load_prototypes_from_file(self, filename, registries):
        raw_prototypes = CardPrototype.load_prototypes(
            filename=filename,
            required_fields=CardPrototype.required_fields,
            prototype_class=CardPrototype
        )

        for card_id, prototype in raw_prototypes.items():
            if card_id in self.card_prototypes:
                raise ValueError(f"Duplicate card ID '{card_id}' found in file '{filename}'.")
            
            # Add the base card prototype
            self.card_prototypes[card_id] = prototype

            # Generate enchanted versions if specified
            if prototype.enchantments is not None:
                self._generate_enchanted_prototypes(card_id, prototype, registries)

    def _generate_enchanted_prototypes(self, base_card_id, prototype, registries):
        for enchantment_id in prototype.enchantments:
            enchantment = registries.enchantments.get_enchantment(enchantment_id)
            enchanted_card = enchantment.create_enchanted_card(prototype, registries.effects)

            if enchanted_card.card_id in self.card_prototypes:
                raise ValueError(f"Duplicate card ID '{enchanted_card.card_id}' generated for '{base_card_id}'.")
            
            self.card_prototypes[enchanted_card.card_id] = enchanted_card

    def create_card(self, card_id: str) -> Card:
        if card_id not in self.card_prototypes:
            raise KeyError(f"Card ID '{card_id}' not found.")
        return self.card_prototypes[card_id].clone()

    def list_cards(self):
        return list(self.card_prototypes.keys())
