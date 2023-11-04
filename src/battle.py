import logging

from src.character import FictionalCharacterVersion
from typing import Dict


class VersusBattleScore:
    def __init__(self, v1: FictionalCharacterVersion, v2: FictionalCharacterVersion, battle_results: Dict[str, int]):
        self.character_version1 = v1
        self.character_version2 = v2
        self.battle_results = battle_results
        self.overall_winner = sum(battle_results.values())

    def __str__(self):
        result = "\n" + ("-" * 50) + "\n"
        result += "Versus Battle:\n"
        result += f"{self.character_version1.character_name} {self.character_version1.version_name} vs. " \
                  f"{self.character_version2.character_name} {self.character_version2.version_name}!\n"
        result += "Begin!\n"
        result += ("-" * 50) + "\n"
        for stat, comp_int in self.battle_results.items():
            result += f"{stat}: {self._get_character_name(comp_int)}\n"
        result += f"\n{self._get_character_name(self.overall_winner)} wins {self._score_string()}!\n"
        result += ("-" * 50) + "\n"
        return result

    def _get_character_name(self, comp_int: int) -> str:
        if comp_int < 0:
            return self.character_version1.character_name
        elif comp_int == 0:
            return "Tie!"
        else:
            return self.character_version2.character_name

    def _score_string(self):
        v1_win_count = list(self.battle_results.values()).count(-1)
        v2_win_count = list(self.battle_results.values()).count(1)
        return f"{max(v1_win_count, v2_win_count)} - {min(v1_win_count, v2_win_count)}"


def versus_battle(version1: FictionalCharacterVersion, version2: FictionalCharacterVersion) -> VersusBattleScore:
    stat_performance = {}

    for stat_name, tier1 in version1.stat_tier_map.items():
        tier2 = version2.stat_tier_map[stat_name]
        if tier1 is None:
            logging.error(f"The stat {stat_name} is not associated with a tier value for first character.")
        elif tier2 is None:
            logging.error(f"The stat {stat_name} is not associated with a tier value for second character.")
        else:
            # Compare the tiers using the __lt__ methods of the Tier class.
            stat_performance[stat_name] = (tier1 < tier2) - (tier1 > tier2)

    return VersusBattleScore(version1, version2, stat_performance)
