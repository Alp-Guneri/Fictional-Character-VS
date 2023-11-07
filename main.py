import json
import logging

from jsonschema import ValidationError

from src.character_parser import CharacterParser
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
    logger = logging.getLogger()
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


def prompt_char_config(tier_parser: TierParser) -> CharacterParser:
    char_config_fpath = input("Please provide the path to character configuration file (Press enter to use default): ")
    if char_config_fpath.strip() == "":
        char_config_fpath = DEFAULT_CHARACTER_CONFIG_PATH
    try:
        with open(char_config_fpath, 'r') as config_file:
            char_config_json = json.load(config_file)
            validate_character_schema(char_config_json)
            res = CharacterParser(tier_parser, char_config_json)
            print("Character configuration successful!\n")
            return res
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
    print("3. List all the configured characters")
    print("4. Parse a character")
    print("5. Display a parsed character")
    print("6. Combine two versions of a parsed character into one")
    print("7. Write parsed character stat(s) to csv file(s) (',' indicates and '-' indicates inclusive range)")
    print("8. Read character(s) from csv file(s)")
    print("9. VS battle between two parsed characters")
    print("10. Search and add a new character")
    print("11. Write the character data to the config file")
    print("12. Quit the application\n")
    print("Please pick an option by its number:", end=" ")
    return prompt_menu_selection()


def prompt_menu_selection() -> int:
    choice_string = input()
    if choice_string.isdigit():
        choice_num = int(choice_string)
        if 0 < choice_num < 13:
            return choice_num
    print("Please pick a valid number:", end=" ")
    return prompt_menu_selection()


class Main:
    def __init__(self):
        self.tier_classifier, self.tier_parser = prompt_tier_config()
        self.character_parser = prompt_char_config(self.tier_parser)
        self.main()

    def main(self):
        choice_num = prompt_main_menu()
        match choice_num:
            case 1:
                print("Hello World!")
            case _:
                print("Not implemented!")
        self.main()


if __name__ == "__main__":
    Main()

    # first_character_name = "Son Goku"
    # second_character_name = "Saitama"
    #
    # t_classifier = TierClassifier()
    #
    # goku = read_from_csv(first_character_name, t_classifier)
    # saitama = read_from_csv(second_character_name, t_classifier)
    #
    # goku_ultra_instinct = next(element for element in goku.character_versions
    #                            if "Perfected Ultra Instinct" in element.version_name)
    #
    # saitama_parallel_timeline = next(element for element in saitama.character_versions
    #                                  if "Parallel Timeline" in element.version_name)
    #
    # print(versus_battle(goku_ultra_instinct, saitama_parallel_timeline))

    # character_name = "Saitama"
    # t_classifier = TierClassifier()
    # t_parser = TierParser(t_classifier)
    # c_parser = CharacterParser(t_parser)
    #
    # saitama = c_parser.parse_character(character_name)
    # write_to_csv(saitama)
