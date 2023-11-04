import json
import requests
import logging
import itertools

from bs4 import BeautifulSoup
from src.character import FictionalCharacter, FictionalCharacterVersion
from src.tier_parser import TierParser
from typing import List
from . import DEFAULT_CHARACTER_CONFIG_PATH


class CharacterParser:
    def __init__(self, tier_parser: TierParser, config_file_path: str = None):
        if config_file_path is None:
            config_file_path = DEFAULT_CHARACTER_CONFIG_PATH
        self._load_config(config_file_path)
        self.tier_parser = tier_parser

    def _load_config(self, config_file_path: str):
        try:
            with open(config_file_path, 'r') as config_file:
                self.config = json.load(config_file)
        except FileNotFoundError:
            raise FileNotFoundError(f"Config file not found: {config_file_path}")

    def _get_web_page(self, character_name: str):
        url = self.config["characters"].get(character_name)
        if not url:
            raise ValueError(f"Character '{character_name}' not found in the configuration.")
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        return response.text

    @staticmethod
    def _flatten_children_text(parent_element):
        # Initialize an empty list to store text from children
        text_list = []

        # Iterate through the children of the parent element
        for child in parent_element.children:
            if child != parent_element.first_element:  # Skip the first element
                text_list.append(child.get_text(strip=True))  # Add the text to the list

        # Join the text from the list into a single string
        flattened_text = ' '.join(text_list)
        return flattened_text

    def _parse_key(self, soup) -> List[str]:
        # Find the "Key:" element in the soup
        key_element = soup.find(text="Key:")
        if key_element:
            # Find the parent paragraph element of the "Key:" element
            parent_paragraph = key_element.find_parent('p')
            if parent_paragraph:
                # Flatten the text from children of the paragraph
                flattened_text = self._flatten_children_text(parent_paragraph)

                # Split the flattened text by the delimiter "|"
                key_list = flattened_text.split('|')
                clean_list = [string.strip() for string in key_list]
                if clean_list[0].startswith("Key: "):
                    clean_list[0] = clean_list[0][6:]
                return clean_list
            else:
                return []
        else:
            return []

    def parse_character(self, character_name: str) -> FictionalCharacter:
        try:
            page_content = self._get_web_page(character_name)
            soup = BeautifulSoup(page_content, 'html.parser')

            # We first begin by parsing the key. This tells us the names of the versions of the character the
            # webpage will be evaluating.
            # character_version_names : List[String]
            character_version_names = self._parse_key(soup)

            # We create a list of character versions that will be updated with relevant stats.
            character_versions = [FictionalCharacterVersion.from_character_and_version_name(character_name, v_name) for
                                  v_name in character_version_names]

            # We want a dictionary that associates each stat name with a list of tiers. Each tier in the list
            # represents the tier score of a different version of the character for a given stat.
            # stats_and_values : Dict[String, List[Tier]]
            stats_and_values = {}

            for stat_name in self.tier_parser.stat_names:
                clean_stat_name = stat_name.strip().replace(" ", "_")

                # The beginning of the try block, where we try to find elements from the webpage
                # that contains the relevant information regarding our character & its versions.
                try:
                    # We find the anchor element that references the stat name.
                    stat_anchor = soup.find('a', href=f"/wiki/{clean_stat_name}")

                    # We find the bold element that contains the anchor element
                    bold_element = stat_anchor.find_parent('b')

                    # We find the parent paragraph element of the bold element
                    parent_paragraph = bold_element.find_parent('p')

                    # Flatten the text from children of the paragraph
                    flattened_stat_information = self._flatten_children_text(parent_paragraph)

                    # Split the flattened text by the delimiter "|"
                    character_version_stat_information_list = flattened_stat_information.split('|')

                    # Initialize an array to store tier values
                    tier_values = []

                    for character_version_stat_information in character_version_stat_information_list:
                        # Parse the value of the key text using the TierParser object
                        tier_value = self.tier_parser \
                            .find_tier_values_from_text(stat_name, character_version_stat_information)[0]

                        if tier_value:
                            # Add the value to the tier_values dictionary
                            tier_values.append(tier_value)

                    # Now that we have tier values, we must check if each character version
                    # has an associated tier value. If not, we elongate the tier_values array.
                    # By elongation a transformation such as from [1,2,3] to [1,1,2,2,3,3] is meant.
                    if len(tier_values) != len(character_version_names):
                        num_repeat = len(character_version_names) // len(tier_values) + 1

                        elongated_tier_values \
                            = list(itertools.chain.from_iterable(itertools.repeat(tier_values, num_repeat)))
                        tier_values = elongated_tier_values[:len(character_version_names)]

                    for i in range(len(tier_values)):
                        character_versions[i].add_tier_value(stat_name, tier_values[i])

                except AttributeError:
                    # Handle AttributeError when an element is missing
                    logging.warning(f"Information for the stat '{stat_name}' could not be parsed from the webpage.")
                    stats_and_values[stat_name] = []

            return FictionalCharacter(character_name, character_versions)

        except Exception as e:
            # If there was an error before parsing the stats of the characters begin, we just return
            # an empty character object.
            logging.error("An error occurred: ", str(e))
            return FictionalCharacter.from_character_name(character_name)
