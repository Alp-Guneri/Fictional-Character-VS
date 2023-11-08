import json
import logging
import re

from jsonschema import ValidationError

from src.character_parser import CharacterParser, CharacterConfig
from src.search import CharacterSearcher
from src.tier import TierClassifier
from src.tier_parser import TierParser
from src.character_io import write_to_csv, read_from_csv
from src.battle import versus_battle
from src.config_validation import validate_tier_schema, validate_character_schema
from src import *


def print_box(message: str, width_margin: int, height_margin: int):
    width = 2 * width_margin + len(message) + 2
    print('-' * width)
    for i in range(height_margin):
        print('|' + (' ' * (width - 2)) + '|')
    print('|' + (' ' * width_margin) + message + (' ' * width_margin) + '|')
    for i in range(height_margin):
        print('|' + (' ' * (width - 2)) + '|')
    print('-' * width + "\n")


def prompt_tier_config() -> (TierClassifier, TierParser):
    tier_config_fpath = input("Please provide the path to tier configuration file (Press enter to use default): ")
    if tier_config_fpath.strip() == "":
        tier_config_fpath = DEFAULT_TIER_CONFIG_PATH
    try:
        with open(tier_config_fpath, 'r') as config_file:
            tier_config_json = json.load(config_file)
            validate_tier_schema(tier_config_json)
            t_classifier = TierClassifier(tier_config_json)
            t_parser = TierParser(t_classifier)
            print("Tier configuration successful!\n")
            return t_classifier, t_parser
    except FileNotFoundError as file_error:
        logging.error(f"File not found: {str(file_error)}.")
        prompt_tier_config()
    except ValidationError as validation_error:
        logging.error(f"The given config file is not valid. {str(validation_error)}")
        prompt_tier_config()


def prompt_char_config(tier_parser: TierParser) -> (CharacterParser, str):
    char_config_fpath = input("Please provide the path to character configuration file (Press enter to use default): ")
    if char_config_fpath.strip() == "":
        char_config_fpath = DEFAULT_CHARACTER_CONFIG_PATH
    try:
        with open(char_config_fpath, 'r') as config_file:
            char_config_json = json.load(config_file)
            validate_character_schema(char_config_json)
            res = CharacterParser(tier_parser, char_config_json)
            print("Character configuration successful!\n")
            return res, char_config_fpath
    except FileNotFoundError as file_error:
        logging.error(f"File not found: {str(file_error)}.")
        prompt_char_config(tier_parser)
    except ValidationError as validation_error:
        logging.error(f"The given config file is not valid. {str(validation_error)}")
        prompt_char_config(tier_parser)


def prompt_main_menu() -> int:
    print_box("Main Menu", 15, 0)
    print("1. List all the stat names")
    print("2. List all the tiers associated with a given stat name")
    print("3. List the names of all the configured characters")
    print("4. List the names all the parsed characters")
    print("5. Parse a character")
    print("6. Display a parsed character")
    print("7. Combine two versions of a parsed character into one")
    print("8. Write parsed character stat(s) to csv file(s) (',' indicates union; '-' indicates inclusive range)")
    print("9. Read character(s) from csv file(s)")
    print("10. VS battle between two parsed characters")
    print("11. Search and add a new character")
    print("12. Write the character data to the config file")
    print("13. Quit the application\n")
    print("Please pick an option by its number:", end=" ")
    return prompt_menu_selection()


def prompt_menu_selection() -> int:
    choice_string = input()
    if choice_string.isdigit():
        choice_num = int(choice_string)
        if 0 < choice_num < 14:
            return choice_num
    print("Please pick a valid number:", end=" ")
    return prompt_menu_selection()


class Main:
    def __init__(self):
        self.tier_classifier, self.tier_parser = prompt_tier_config()
        self.character_parser, self.char_config_fpath = prompt_char_config(self.tier_parser)
        # self.configured_characters: List[CharacterConfig]
        self.configured_characters = self.character_parser.character_configs
        # self.parsed_characters: List[FictionalCharacter]
        self.parsed_characters = []

        self.main()

    def find_parsed_character(self, character_name: str):
        res = None
        for parsed_char in self.parsed_characters:
            if parsed_char.character_name == character_name:
                res = parsed_char
                break
        return res

    def main(self):
        choice_num = prompt_main_menu()
        match choice_num:
            case 1:
                print(str(self.tier_classifier.get_all_stat_names()))
            case 2:
                stat_name = input("Please enter the stat name: ")
                tiers = self.tier_classifier.get_all_tiers_of_stat(stat_name)
                print('\n'.join([str(tier) for tier in tiers]))
            case 3:
                if len(self.configured_characters) == 0:
                    print("No configured characters found!")
                else:
                    for index, configured_char in enumerate(self.configured_characters):
                        print(f"#{index + 1}: {configured_char.character_name}")
            case 4:
                if len(self.parsed_characters) == 0:
                    print("No parsed characters found!")
                else:
                    for index, parsed_char in enumerate(self.parsed_characters):
                        print(f"#{index + 1}: {parsed_char.character_name}")
            case 5:
                character_name = input("Please enter the character's name: ")
                if character_name in [parsed_char.character_name for parsed_char in self.parsed_characters]:
                    print("The character is already parsed!")
                elif character_name not in [conf_char.character_name for conf_char in self.configured_characters]:
                    print("The character is not configured!")
                else:
                    parsed_char = self.character_parser.parse_character(character_name)
                    self.parsed_characters.append(parsed_char)
                    print("Character parsing successful!\n\n")
            case 6:
                character_name = input("Please enter the character's name: ")
                parsed_character = self.find_parsed_character(character_name)
                if parsed_character:
                    print(parsed_character)
                else:
                    print("Character not found!")
            case 7:
                character_name1 = input("Please enter the first character's name: ")
                parsed_char1 = self.find_parsed_character(character_name1)
                if not parsed_char1:
                    print("Character not found!")
                else:
                    character_name2 = input("Please enter the second character's name: ")
                    parsed_char2 = self.find_parsed_character(character_name2)
                    if not parsed_char2:
                        print("Character not found!")
                    else:
                        self.parsed_characters.remove(parsed_char1)
                        self.parsed_characters.remove(parsed_char2)
                        self.parsed_characters.append(parsed_char1.add_versions_from_character(parsed_char2))
            case 8:
                try:
                    input_indices = input("Please enter the numbers of the character you want to select: ")
                    indices = input_indices.split(',')
                    chosen_characters = []
                    for num_or_range in indices:
                        is_valid = re.search("([0-9]+(\s*)-(\s*)[0-9]+)|([0-9]+)", num_or_range)
                        if not is_valid:
                            print(f"Invalid input: {num_or_range}")
                        else:
                            if '-' in num_or_range:
                                split_range = num_or_range.split('-')
                                range_begin = int(split_range[0]) - 1
                                range_end = int(split_range[1]) - 1
                                if 0 < range_begin < range_end < len(self.parsed_characters):
                                    for i in range(range_begin, range_end + 1):
                                        chosen_characters.append(self.parsed_characters[i])
                                else:
                                    print(f"Range input out of bounds: {num_or_range}")
                            else:
                                char_index = int(num_or_range) - 1
                                if 0 < char_index < len(self.parsed_characters):
                                    chosen_characters.append(self.parsed_characters[char_index])
                                else:
                                    print(f"Number input out of bounds: {num_or_range}")
                    for character in chosen_characters:
                        write_to_csv(character)
                except IOError:
                    print("Error while writing characters to the file.")
            case 9:
                fpath = input("Please provide the path to a csv file or a directory containing csv files: ")
                if os.path.isfile(fpath):
                    parsed_char = read_from_csv(fpath, self.tier_classifier)
                    self.parsed_characters.append(parsed_char)
                    print(f"Character \"{parsed_char.character_name}\" was read from csv successfully!")
                elif os.path.isdir(fpath):
                    parsed_chars = []
                    for csv_file in os.listdir(fpath):
                        if os.path.isfile(csv_file) and re.search("^([a-z]|[A-Z]|[0-9])+\.csv$", csv_file):
                            parsed_chars.append(read_from_csv(csv_file, self.tier_classifier))
                    self.parsed_characters.extend(parsed_chars)
                else:
                    print("The given path is invalid!")
            case 10:
                character_name1 = input("Please enter the first character's name: ")
                parsed_char1 = self.find_parsed_character(character_name1)
                if not parsed_char1:
                    print("Character not found!")
                else:
                    print(parsed_char1)
                    v_name1 = input("\nPlease enter a version name: ")
                    if v_name1 not in [version.version_name for version in parsed_char1.character_versions]:
                        print("Version not found!")
                    else:
                        version_1 = next(filter(lambda v: v.version_name == v_name1, parsed_char1.character_versions))
                        character_name2 = input("Please enter the second character's name: ")
                        parsed_char2 = self.find_parsed_character(character_name2)
                        if not parsed_char2:
                            print("Character not found!")
                        else:
                            print(parsed_char2)
                            v_name2 = input("\nPlease enter a version name: ")
                            if v_name1 not in [version.version_name for version in parsed_char2.character_versions]:
                                print("Version not found!")
                            else:
                                version_2 = next(
                                    filter(lambda v: v.version_name == v_name2, parsed_char2.character_versions))
                                print(versus_battle(version_1, version_2))
            case 11:
                char_name = input("Please enter the name of character: ")
                searcher = CharacterSearcher(char_name)
                searcher.search_character()
                character_found = False
                while not character_found:
                    print("(C)hoose character")
                    print("(P)revious page")
                    print("(N)ext page")
                    print("(G)o to page by number")
                    user_input = input("Please make a choice: ")
                    match user_input[0]:
                        case 'C':
                            char_num = int(input("Please enter the character's number: "))
                            if 0 < char_num <= len(searcher.results):
                                search_result = searcher.results[char_num - 1]
                                self.configured_characters.append(
                                    CharacterConfig(search_result.character_name, search_result.webpage_url))
                                character_found = True
                        case 'P':
                            searcher.get_prev_page()
                        case 'N':
                            searcher.get_next_page()
                        case 'G':
                            page_num = int(input("Please enter the page number you would like to go to: "))
                            searcher.get_page_by_num(page_num)
            case 12:
                with open(self.char_config_fpath, 'w') as outfile:
                    json.dump(self.configured_characters, outfile)
            case 13:
                exit(0)
            case _:
                print("Not implemented!")
        self.main()


if __name__ == "__main__":
    Main()
