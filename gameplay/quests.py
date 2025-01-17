"""
This module defines the Quest and QuestRegistry classes.
"""
from utils.utils import load_json
from gameplay.encounters import Encounter

class Quest:
    """
    This class represents a series of encounters.
    """
    def __init__(
            self, quest_id, description, encounters, enemy_cache, card_cache,
            status_registry
            ):
        """
        Initialize a new Quest.
        """
        self.quest_id = quest_id
        self.description = description
        self.encounters = []
        for encounter in encounters:
            enemy = enemy_cache.create_enemy(
                encounter, card_cache, status_registry
                )
            self.encounters.append(Encounter(enemy))

class QuestRegistry:
    """
    This class holds quest data loaded from JSON.
    """
    def __init__(self, quests_path, enemy_cache, card_cache, status_registry):
        """
        Initialize a new QuestRegistry.
        """
        self.quests = []
        quest_data = load_json(quests_path)
        for quest_id, quest_details in quest_data.items():
            description = quest_details.get(
                "DESCRIPTION", "No description provided."
                )
            encounters = quest_details.get("ENCOUNTERS", [])
            quest = Quest(
                quest_id, description, encounters, enemy_cache, card_cache,
                status_registry
                )
            self.quests.append(quest)
