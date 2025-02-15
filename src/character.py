import logging

from typing import Dict, List
from src.tier import Tier


class FictionalCharacterVersion:
    def __init__(self, character_name: str, version_name: str, stat_tier_map: Dict[str, Tier]):
        self.character_name = character_name
        self.version_name = version_name
        self.stat_tier_map = stat_tier_map

    @classmethod
    def from_character_and_version_name(cls, character_name: str, version_name: str):
        return cls(character_name, version_name, {})

    def add_tier_value(self, stat_name: str, tier_value: Tier):
        self.stat_tier_map[stat_name] = tier_value

    def remove_stat(self, stat_name: str):
        del self.stat_tier_map[stat_name]

    def __str__(self):
        return f"Character: {self.character_name}, Version: {self.version_name}\n" \
               f"{[str(tier) for tier in self.stat_tier_map.values()]}"


# noinspection PyRedeclaration
class FictionalCharacter:
    def __init__(self, character_name: str, character_versions: List[FictionalCharacterVersion]):
        self.character_name = character_name
        self.character_versions = character_versions

    @classmethod
    def from_character_name(cls, character_name: str):
        return cls(character_name, [])

    def get_character_versions_by_name(self, v_name: str) -> List[FictionalCharacterVersion]:
        return list(filter(lambda v: v_name in v.version_name, self.character_versions))

    def add_character_version(self, version: FictionalCharacterVersion):
        self.character_versions.append(version)

    def remove_character_version(self, version: FictionalCharacterVersion):
        self.character_versions.remove(version)

    def add_versions_from_character(self, character):
        if self.character_name != character.character_name:
            logging.warning(f"Merging versions from \"{character.character_name}\" into \"{self.character_name}\".\n"
                            f"This is usually done to merge character objects that refer to the same character.")
        self.character_versions.extend(character.character_versions)

    def __str__(self):
        return "\n".join([str(version) for version in self.character_versions])
