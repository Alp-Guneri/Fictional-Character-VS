import json
import requests
from bs4 import BeautifulSoup
from tier_parser import TierParser
from typing import List
import csv
import itertools
import os

class CharacterParser:
    def __init__(self, config_file_path: str, character_name: str, tier_parser: TierParser):
        self._load_config(config_file_path)
        self.character_name = character_name
        self.tier_parser = tier_parser
        self.url = self.config["characters"].get(character_name)
        if not self.url:
            raise ValueError(f"Character '{character_name}' not found in the configuration.")

    def _load_config(self, config_file_path: str):
        try:
            with open(config_file_path, 'r') as config_file:
                self.config = json.load(config_file)
        except FileNotFoundError:
            raise FileNotFoundError(f"Config file not found: {config_file_path}")

    def _get_web_page(self):
        response = requests.get(self.url)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        return response.text

    def _flatten_children_text(self, parent_element):
        # Initialize an empty list to store text from children
        text_list = []

        # Iterate through the children of the parent element
        for child in parent_element.children:
            if child != parent_element.first_element:  # Skip the first element
                text_list.append(child.get_text(strip=True))  # Add the text to the list

        # Join the text from the list into a single string
        flattened_text = ' '.join(text_list)
        return flattened_text

    def parse_key(self, soup) -> List[str]:
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

    # Utility function for parsing and writing the output to a csv file.
    def parse_and_write(self, output_file_path: str = None):
        self.parse_character_stats()
        self.write_to_csv(output_file_path)

    def parse_character_stats(self):
        try:
            page_content = self._get_web_page()
            soup = BeautifulSoup(page_content, 'html.parser')

            # We first begin by parsing the key. This tells us the names of the versions of the character the
            # webpage will be evaluating.
            # character_versions : List[String]
            self.character_versions = self.parse_key(soup)

            # We want a dictionary that associates each stat name with a list of tiers. Each tier in the list
            # represents the tier score of a different version of the character for a given stat.
            # stats_and_values : Dict[String, List[Tier]]
            stats_and_values = {}

            for stat_name in self.tier_parser.stat_names:
                clean_stat_name = stat_name.strip().replace(" ", "_")
                stat_anchor = soup.find('a', href=f"/wiki/{clean_stat_name}")

                if stat_anchor:
                    bold_element = stat_anchor.find_parent('b')

                    if bold_element:
                        # Find the parent paragraph element of the bold element
                        parent_paragraph = bold_element.find_parent('p')

                        if parent_paragraph:
                            # Flatten the text from children of the paragraph
                            flattened_stat_information = self._flatten_children_text(parent_paragraph)

                            # Split the flattened text by the delimiter "|"
                            character_version_stat_information_list = flattened_stat_information.split('|')

                            # Initialize an array to store tier values
                            tier_values = []

                            for character_version_stat_information in character_version_stat_information_list:
                                # Parse the value of the key text using the TierParser object
                                tier_value = self.tier_parser\
                                    .find_tier_values_from_text(stat_name, character_version_stat_information)[0]

                                if tier_value:
                                    # Add the value to the tier_values dictionary
                                    tier_values.append(tier_value)

                            # Now that we have tier values, we must check if each character version
                            # has an associated tier value. If not, we elongate the tier_values array.
                            # By elongation a transformation such as from [1,2,3] to [1,1,2,2,3,3] is meant.
                            if len(tier_values) != len(self.character_versions):
                                num_repeat = len(self.character_versions) // len(tier_values) + 1

                                elongated_tier_values \
                                    = list(itertools.chain.from_iterable(itertools.repeat(tier_values, num_repeat)))
                                tier_values = elongated_tier_values[:len(self.character_versions)]

                            stats_and_values[stat_name] = tier_values

            self.stats_and_values = stats_and_values

        except Exception as e:
            # Handle any other exceptions here, log the error, and decide what to do
            # You can raise a custom exception or return None
            print("An error occurred:", str(e))
            return None

    def write_to_csv(self, output_file_path: str = None):
        file_name = self.character_name.strip().replace(" ", "-")
        if output_file_path is None:
            output_file_path = f"out/{file_name}.csv"
        directory = os.path.dirname(output_file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)

        # Prepare the data for writing to the CSV file
        data = []

        # Add the legend in the first row
        legend = ["Character Version"] + list(self.tier_parser.stat_names)
        data.append(legend)

        # Loop through character versions and add data for each version
        for i in range(len(self.character_versions)):
            character_version = self.character_versions[i]
            row = [character_version] + [self.stats_and_values[stat_name][i].synonyms[0]
                                         for stat_name in self.tier_parser.stat_names]
            data.append(row)

        # Write the data to a CSV file
        with open(output_file_path, 'w', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerows(data)