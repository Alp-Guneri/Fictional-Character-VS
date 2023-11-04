from typing import Dict, List
from tier_parser import Tier


# noinspection PyRedeclaration
class FictionalCharacterVersion:
    def __init__(self, version_name: str):
        self.version_name = version_name
        self.stat_tier_map = {}

    def __init__(self, version_name: str, stat_tier_map: Dict[str, Tier]):
        self.version_name = version_name
        self.stat_tier_map = stat_tier_map

    def add_tier_value(self, stat_name: str, tier_value: Tier):
        self.stat_tier_map[stat_name] = tier_value

    def __str__(self):
        return f"Character Version: {self.version_name}\n{[str(tier) for tier in self.stat_tier_map.values()]}"


# noinspection PyRedeclaration
class FictionalCharacter:
    def __init__(self, character_name: str):
        self.character_name = character_name
        self.character_versions = []

    def __init__(self, character_name: str, character_versions: List[FictionalCharacterVersion]):
        self.character_name = character_name
        self.character_versions = character_versions

    def add_character_version(self, version: FictionalCharacterVersion):
        self.character_versions.append(version)

    def remove_character_version(self, version: FictionalCharacterVersion):
        self.character_versions.remove(version)

    def __str__(self):
        versions_str = "\n".join([str(version) for version in self.character_versions])
        return f"Character: {self.character_name}\n{versions_str}"


# Usage example:
example_name = "Character A"

version_1_stats = {"Intelligence": Tier("Intelligence", ["Average"]), "Speed": Tier("Speed", ["Athletic"])}
version_2_stats = {"Intelligence": Tier("Intelligence", ["Above Average"]), "Speed": Tier("Speed", ["Peak Human"])}
example_version_1 = FictionalCharacterVersion("Anime Version", version_1_stats)
example_version_2 = FictionalCharacterVersion("Manga Version", version_2_stats)

example_character = FictionalCharacter(example_name, [example_version_1, example_version_2])

print(example_character)
