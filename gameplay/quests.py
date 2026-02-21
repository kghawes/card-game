"""
This module defines the Quest and QuestRegistry classes.
"""
import random
from utils.utils import load_json
from gameplay.encounters import Encounter

class Quest:
    """
    This class represents a series of encounters.
    """
    def __init__(
            self, quest_id, description, encounters,
            registries
            ):
        """
        Initialize a new Quest.
        """
        self.quest_id = quest_id
        self.description = description
        self.encounters = []
        for encounter in encounters:
            enemy = registries.enemies.create_enemy(
                encounter, registries, None
                )
            self.encounters.append(Encounter(enemy))

class QuestRegistry:
    """
    This class holds quest data loaded from JSON.
    """
    def __init__(
            self, quests_path, enemy_groups_path, registries
            ):
        """
        Initialize a new QuestRegistry.
        """
        self.quests = []
        quest_data = load_json(quests_path)
        enemy_group_data = load_json(enemy_groups_path)
        for quest_id, quest_details in quest_data.items():
            description = quest_details.get(
                "DESCRIPTION", "No description provided."
                )
            encounters = quest_details.get("ENCOUNTERS", [])
            encounters = self.setup_encounters(encounters, enemy_group_data)
            quest = Quest(
                quest_id, description, encounters,
                registries
                )
            self.quests.append(quest)

    def setup_encounters(self, encounter_data, enemy_groups) -> list:
        """
        Randomly select enemies to encounter in the quest.
        """
        encounters = []
        boss = encounter_data.pop()
        for encounter in encounter_data:
            enemy_table = enemy_groups.get(encounter, {})
            enemies, weights = zip(*list(enemy_table.items()))
            enemy = random.choices(enemies, weights=weights, k=1)[0]
            encounters.append(enemy)
        encounters.append(boss)
        return encounters
