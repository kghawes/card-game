from utils.utils import load_json
from gameplay.encounters import Encounter

class Quest:
    def __init__(self, quest_id, description, encounters, enemy_cache):
        self.description = description
        self.encounters = []
        for encounter in encounters:
            self.encounters.append()

class QuestCache:
    def __init__(self, quests_path, enemy_cache):
        self.quests = []
        quest_data = load_json(quests_path)
        for quest_id, quest_details in quest_data.items():
            description = quest_details.get("DESCRIPTION", "No description provided.")
            encounters = quest_details.get("ENCOUNTERS", [])
            self.quests.append(Quest(quest_id, description, encounters, enemy_cache))