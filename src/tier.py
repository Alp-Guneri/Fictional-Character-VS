import copy

from typing import List


class Tier:
    def __init__(self, stat_name: str, tier_value: int, synonyms: List[str]):
        self.stat_name = stat_name
        self.tier_value = tier_value
        self.synonyms = synonyms
        self.default_tier_name = synonyms[0]

    def __lt__(self, other):
        return self.tier_value < other.tier_value

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Tier):
            # Compare stat_name and synonyms
            return self.stat_name == other.stat_name and self.tier_value == other.tier_value
        elif isinstance(other, str):
            # Check if the string is in the synonyms list
            return other in self.synonyms
        else:
            return False

    def __str__(self) -> str:
        return f"Tier(stat_name: {self.stat_name}, tier: {self.default_tier_name}, value: {self.tier_value})"


class TierClassifier:

    def __init__(self, config_file_json):
        # self.config: Dict[String, Any]
        self.config = config_file_json
        # self.stat_names: [str]
        self.stat_names = []
        # self.stat_name_to_all_tiers: Dict[String, List[Tier]]
        self.stat_name_to_all_tiers = {}

        self._read_config()

    def _read_config(self):
        # stat_names : List[str]
        self.stat_names = self.config.get("statNames", [])

        default_stat_tiers = self._read_all_tiers_of_stat("tier")
        for stat_name in self.stat_names:
            if stat_name in self.config:
                all_tiers = self._read_all_tiers_of_stat(stat_name)
                self.stat_name_to_all_tiers[stat_name] = all_tiers
            else:
                default_stat_tiers_copy = copy.deepcopy(default_stat_tiers)
                for tier in default_stat_tiers_copy:
                    tier.stat_name = stat_name
                self.stat_name_to_all_tiers[stat_name] = default_stat_tiers_copy

    def _read_all_tiers_of_stat(self, stat_name: str) -> List[Tier]:
        # stat_tiers : List[str] OR List[List[str]]
        stat_tiers = self.config[stat_name]["tiers"]
        # tiers_list : List[Tier]
        tiers_list = []
        tier_value_counter = 0
        for stat_tier in stat_tiers:
            stat_tier_synonyms = []
            if isinstance(stat_tier, str):
                stat_tier_synonyms = [stat_tier]
            else:
                stat_tier_synonyms.extend(stat_tier)
            tier_value_counter += 1
            tier_object = Tier(stat_name, tier_value_counter, stat_tier_synonyms)
            tiers_list.append(tier_object)
        return tiers_list

    def is_valid_tier(self, stat_name: str, tier_name: str) -> bool:
        return tier_name in self.stat_name_to_all_tiers[stat_name]

    def get_tier_from_name(self, stat_name: str, tier_name: str) -> Tier:
        index = self.stat_name_to_all_tiers[stat_name].index(tier_name)
        return self.stat_name_to_all_tiers[stat_name][index]

    def get_all_stat_names(self) -> [str]:
        return self.stat_names

    def get_all_tiers_of_stat(self, stat_name: str):
        if stat_name not in self.stat_names:
            return []
        return self.stat_name_to_all_tiers[stat_name]
