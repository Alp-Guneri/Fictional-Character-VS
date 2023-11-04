from typing import Dict, List
from src.tier import Tier


class FictionalCharacterVersion:
    def __init__(self, version_name: str, stat_tier_map: Dict[str, Tier]):
        self.version_name = version_name
        self.stat_tier_map = stat_tier_map

    @classmethod
    def from_version_name(cls, version_name: str):
        return cls(version_name, {})

    def add_tier_value(self, stat_name: str, tier_value: Tier):
        self.stat_tier_map[stat_name] = tier_value

    def remove_stat(self, stat_name: str):
        del self.stat_tier_map[stat_name]

    def __str__(self):
        return f"Character Version: {self.version_name}\n{[str(tier) for tier in self.stat_tier_map.values()]}"


# noinspection PyRedeclaration
class FictionalCharacter:
    def __init__(self, character_name: str, character_versions: List[FictionalCharacterVersion]):
        self.character_name = character_name
        self.character_versions = character_versions

    @classmethod
    def from_character_name(cls, character_name: str):
        return cls(character_name, [])

    def add_character_version(self, version: FictionalCharacterVersion):
        self.character_versions.append(version)

    def remove_character_version(self, version: FictionalCharacterVersion):
        self.character_versions.remove(version)

    def __str__(self):
        versions_str = "\n".join([str(version) for version in self.character_versions])
        return f"Character: {self.character_name}\n{versions_str}"
