RESOURCE_COLORS = {
    "HEALTH": [0.68, 0.281, 0.168, 1.0], # red
    "STAMINA": [0.0, 0.574, 0.293, 1.0], # green
    "MAGICKA": [0.262, 0.305, 0.566, 1.0], # blue
    "NONE": [0.0, 0.0, 0.0, 0.0] # transparent
}

CARD_TYPE_COLORS = {
    "WEAPON": {
        "border": [0.882, 0.227, 0.306, 1.0], # red
        "cost": RESOURCE_COLORS["STAMINA"]
    },
    "ITEM": {
        "border": [0.376, 0.631, 0.702, 1.0], # light blue
        "cost": RESOURCE_COLORS["NONE"]
    },
    "CONSUMABLE": {
        "border": [0.702, 0.376, 0.631, 1.0], # pink
        "cost": RESOURCE_COLORS["NONE"]
    },
    "SPELL": {
        "border": [0.447, 0.376, 0.702, 1.0], # purple-blue
        "cost": RESOURCE_COLORS["MAGICKA"]
    },
    "SKILL": {
        "border": [0.471, 0.702, 0.376, 1.0], # green
        "cost": RESOURCE_COLORS["STAMINA"]
    },
    "ARMOR": {
        "border": [0.961, 0.616, 0.204, 1.0], # orange-yellow
        "cost": RESOURCE_COLORS["STAMINA"]
    },
    "CARD_BACK": {
        "border": [0.656, 0.547, 0.469, 1.0], # tan
        "cost": RESOURCE_COLORS["NONE"]
    }
}
