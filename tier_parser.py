from typing import List

from tier import Tier, TierClassifier


class TierParser:
    def __init__(self, tier_classifier: TierClassifier):
        self.tier_classifier = tier_classifier
        self.stat_name_to_tier_trie = {}
        self.stat_names = tier_classifier.get_all_stat_names()

        for stat_name in self.stat_names:
            all_tiers = tier_classifier.get_all_tiers_of_stat(stat_name)
            self.stat_name_to_tier_trie[stat_name] = TierTrie(all_tiers)

    def find_tier_values_from_text(self, stat_name, text) -> List[Tier]:
        stat_tier_trie = self.stat_name_to_tier_trie[stat_name]
        found_tier_strings = stat_tier_trie.find_tier_strings(text)

        return [self.tier_classifier.get_tier_from_name(stat_name, tier_name) for tier_name in found_tier_strings]

    def __str__(self) -> str:
        result = f"Parser successfully configured for the following stats: {str(self.tier_classifier.stat_names)}.\n\n"
        return result


class TierTrieNode:
    def __init__(self):
        self.children = {}
        self.is_end_of_tier = False


class TierTrie:
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
