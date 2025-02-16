# Journeys in the Land of Ash

## Overview
***Journeys in the Land of Ash*** ("Land of Ash") is a single-player roguelike deckbuilding game inspired by *Slay the Spire*, set in the world of *The Elder Scrolls III: Morrowind*. Players take on the role of a new recruit in one of the major guilds, navigating a series of encounters and quests while building their deck, battling enemies, and acquiring powerful cards.

## Features
- **Turn-based card combat**: Engage in strategic battles where every action is a card.
- **Deckbuilding progression**: Acquire new cards, optimize your deck, and develop unique playstyles.
- **Dual-resource system**: Manage both stamina and magicka for tactical gameplay.
- **Exp and leveling**: Increase health, magicka, or stamina each level.
- **Dynamic status effects**: Apply buffs, debuffs, and ongoing effects.
- **Guild-based classes**: Choose from Fighters Guild, Thieves Guild, or Mages Guild, each with unique starting decks and abilities.
- **Randomized encounters**: Battle various enemies, find treasures, and experience unique events.
- **Persistent unlocks**: Earn rewards after defeat to improve future runs.

## Gameplay
The game follows a loop of:
1. **Start in Town**: Adjust deck, visit merchants, and select quests.
2. **Embark on a Quest**: Progress through enemy encounters, events, and treasure.
3. **Turn-Based Combat**: Play cards to attack, defend, and use abilities.
4. **Gain Rewards**: Earn gold, experience, and new cards.
5. **Return to Town**: Use rewards to strengthen your deck for the next quest.
6. **Defeat and Restart**: Death is the permanent end of that character, and unlocks a card for future runs.

## Card Types
A card has a **type**, a **cost** to play, and one or more **effects**.
- **Weapon** (stamina): Deals physical damage, may have enchantments.
- **Armor** (stamina): Provides defense and other effects.
- **Skill** (stamina): Various non-damage effects.
- **Spell** (magicka): Powerful and versatile magic-based cards.
- **Item** (free): Rare cards with unique effects.
- **Consumable** (free, single-use): Potions and scrolls with potent effects.

## Statuses and Effects
**Effects** take place immediately upon playing a card. Some notable effects include **inflicting damage**, **drawing cards**, and **applying statuses** to either yourself or the enemy.

**Statuses** impact combat dynamically. Some key examples:
- **Defense**: Reduces incoming damage.
- **Poison**: Deals damage over time.
- **Fortify [Stat]**: Boosts a resource or effect.
- **Weakness [Damage Type]**: Increases damage taken.
- **Reflect**: Bounces elemental damage back at the attacker.
- **Disease**: Limits the number of cards you can play in a turn.

Statuses decay over time and can also be removed through effects.

## Enemies
Enemies come with their own decks and abilities, ranging from **Cliff Racers** to **Dremora Lords**. They play cards similarly to the player, drawing, attacking, and defending each turn.

## Development
The game is structured with modular, object-oriented programming in Python. Key components:
- **Card System** (`cards.py` and `card_manager.py`): Defines card behavior and effects.
- **Combat System** (`combat_manager.py` and `combatant.py`): Handles turn-based battle logic.
- **Status System** (`statuses.py` and `status_manager.py`): Manages buffs, debuffs, and conditions.
- **Enemy System** (`enemies.py`): Generates enemies and their decks.
- **Quest System** (`quests.py`): Controls quest progression and encounters.
- **Town & Merchant** (`town.py`, `library.py`, etc.): Allows deck management and purchasing new cards.

Data including cards and enemies are defined in JSON files.

### GUI
The game uses Kivy for 2D graphics. See the [Kivy documentation](https://kivy.org/doc/stable/). This is a declarative system using widgets and .kv files for styling.

GUI structure:
- Game
  - Kivy app
    - Window
      - Screens (a collection of widgets and logic for a particular mode such as combat or shop)
        - Widgets (and their widget children) -> defined partly in .py and partly in .kv
          - Canvas (this is where shapes, colors, and images are drawn) -> defined primarily in .kv

## Getting Started
### Prerequisites
- Python 3.x
- Kivy 2.3.1

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/kghawes/card-game.git
   cd card-game
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the game:
   ```bash
   python main.py
   ```

Tips: It is recommended to create a virtual environment for the project. 

## Roadmap
- **GUI Implementation**: Transition from text-based to graphical interface.
- **Core Features**: Implement the merchant and other critical systems.
- **Playtesting and Balancing**: Iteratively test different strategies and adjust cards and enemies to ensure appropriate challenge.
- **Visuals and Sounds**: Add art, visual effects, and sound effects to enhance the gaming experience.
- **Expanded Content**: More quests, enemies, events, and cards.
- **Sophisticated AI**: Smarter enemy behavior and deck strategies.

## License
This is a personal project and is not intended for commercial release. The setting and lore are based on *The Elder Scrolls III: Morrowind*, owned by Bethesda Softworks. Some content or assets may be based on copyrighted material owned by Bethesda Softworks. This game should be considered a work of parody. Original code may be freely reused with credit to this project.

## Contact
For feedback or contributions, open an issue on GitHub.

