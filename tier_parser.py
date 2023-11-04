import json
from typing import List


class Tier:
    def __init__(self, stat_name: str, synonyms: List[str]):
        self.stat_name = stat_name
        self.synonyms = synonyms
        self.default_tier_name = synonyms[0]

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Tier):
            # Compare stat_name and synonyms
            return self.stat_name == other.stat_name and self.synonyms == other.synonyms
        elif isinstance(other, str):
            # Check if the string is in the synonyms list
            return other in self.synonyms
        else:
            return False

    def __str__(self) -> str:
        return f"Tier(stat_name: {self.stat_name}, value: {self.default_tier_name})"


class TierParser:
    def __init__(self, config_file_path: str):
        self._load_config(config_file_path)

    def _load_config(self, config_file_path):
        try:
            with open(config_file_path, 'r') as config_file:
                self.config = json.load(config_file)
        except FileNotFoundError:
            raise Exception(f"Config file not found: {config_file}")

        # stat_names : List[str]
        self.stat_names = self.config.get("statNames", [])

        # stats : Dict[String, List[Tier]]
        self.stats = {}

        default_stat_tiers = self._read_all_tiers_of_stat("tier")
        for stat_name in self.stat_names:
            if stat_name in self.config:
                all_tiers = self._read_all_tiers_of_stat(stat_name)
                self.stats[stat_name] = all_tiers
            else:
                self.stats[stat_name] = default_stat_tiers

    def _read_all_tiers_of_stat(self, stat_name: str) -> List[Tier]:
        # stat_tiers : List[str] OR List[List[str]]
        stat_tiers = self.config[stat_name]["tiers"]
        # tiers_list : List[Tier]
        tiers_list = []
        for stat_tier in stat_tiers:
            stat_tier_synonyms = []
            if isinstance(stat_tier, str):
                stat_tier_synonyms = [stat_tier]
            else:
                stat_tier_synonyms.extend(stat_tier)
            tier_object = Tier(stat_name, stat_tier_synonyms)
            tiers_list.append(tier_object)
        return tiers_list

    def is_valid_tier(self, stat_name, tier):
        return tier.strip() in self.stats[stat_name.strip()]

    def find_tier_values_from_text(self, stat_name, text) -> List[Tier]:
        # stat_tiers: List[Tier]
        stat_tiers = self.stats[stat_name.strip()]

        tier_trie = TierTrie(stat_tiers)
        found_tier_strings = tier_trie.find_tier_strings(text)

        found_tiers = []
        for t_string in found_tier_strings:
            for tier in stat_tiers:
                if tier == t_string:
                    found_tiers.append(tier)
                    break

        return found_tiers

    def __str__(self) -> str:
        result = f"Parser successfully configured for the following stats: {str(self.stat_names)}.\n\n"
        for key, value in self.stats.items():
            result += f"{key}:\n"
            for tier in value:
                result += f"  - {str(tier)}\n"
        return result


class TierTrieNode:
    def __init__(self):
        self.children = {}
        self.is_end_of_tier = False


# noinspection PyRedeclaration
class TierTrie:
    def __init__(self):
        self.root = TierTrieNode()

    def __init__(self, tiers: List[str]):
        self.root = TierTrieNode()
        for t in tiers:
            self.insert_tier(t)

    def __init__(self, tiers: List[Tier]):
        self.root = TierTrieNode()
        for t in tiers:
            for syn in t.synonyms:
                self.insert_tier(syn)

    def insert_tier(self, tier: str):
        node = self.root
        for char in tier:
            if char not in node.children:
                node.children[char] = TierTrieNode()
            node = node.children[char]
        node.is_end_of_tier = True

    def find_tier_strings(self, text: str) -> List[str]:
        tiers = []
        i = 0

        while i < len(text):
            node = self.root
            k_length = 0
            curr_longest_word = None
            if text[i] not in node.children:
                i += 1
            else:
                for j in range(i, len(text)):
                    curr_char = text[j]
                    if curr_char in node.children:
                        node = node.children[curr_char]
                        if node.is_end_of_tier:
                            k_length = j - i
                            curr_longest_word = text[i: j + 1]
                    else:
                        break
                if k_length > 0:
                    tiers.append(curr_longest_word)
                    i = i + k_length
                else:
                    i += 1
        return tiers


__all__ = ['Tier', 'TierParser']
