"""
This module defines constants needed for the gui.
"""

RESOURCE_COLORS = {
    "HEALTH": [0.68, 0.281, 0.168, 1.0], # red
    "STAMINA": [0.0, 0.574, 0.32, 1.0], # green
    "MAGICKA": [0.262, 0.305, 0.566, 1.0], # blue
    "NONE": [0.44, 0.44, 0.44, 1.0] # grey
}

RESOURCE_INDICATOR_OFFSETS = {
    "LOWER_RIGHT": [15, 38, 2, 38, 2, 25],
    "UPPER_LEFT": [38, 15, 38, 2, 25, 2],
    "NONE": [0, 0, 0, 0, 0, 0]
}

CARD_TYPE_COLORS = {
    "WEAPON": {
        "border": [0.47, 0.17, 0.21],#[0.882, 0.227, 0.306, 1.0], # red
        "resource": "STAMINA",
        "indicator": "LOWER_RIGHT"
    },
    "ITEM": {
        "border": [0.376, 0.631, 0.702, 1.0], # blue
        "resource": "NONE",
        "indicator": "NONE"
    },
    "CONSUMABLE": {
        "border": [0.75, 0.38, 0.63, 1.0], # pink
        "resource": "NONE",
        "indicator": "NONE"
    },
    "SPELL": {
        "border": [0.547, 0.375, 0.699, 1.0], # purple
        "resource": "MAGICKA",
        "indicator": "UPPER_LEFT"
    },
    "SKILL": {
        "border": [0.641, 0.699, 0.375, 1.0], # green
        "resource": "STAMINA",
        "indicator": "LOWER_RIGHT"
    },
    "ARMOR": {
        "border": [0.961, 0.616, 0.204, 1.0], # orange
        "resource": "STAMINA",
        "indicator": "LOWER_RIGHT"
    }
}

CARD_BORDER_RADIUS = [15, 15, 15, 15]
CARD_BODY_RADIUS = [13, 13, 13, 13]

TOOLTIP_WIDTH = 360

STATUS_ICONS_PATH = "gui/assets/statusimages/{}.png"
