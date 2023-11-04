from src.character_parser import CharacterParser
from src.tier import TierClassifier
from src.tier_parser import TierParser
from src.character_io import write_to_csv, read_from_csv

if __name__ == "__main__":
    character_name = "Son Goku"

    t_classifier = TierClassifier()
    goku = read_from_csv(character_name, t_classifier)

    print(goku)
    # t_parser = TierParser(t_classifier)
    # c_parser = CharacterParser(character_config_file_path, t_parser)
    #
    # goku = c_parser.parse_character(character_name)
    # write_to_csv(goku, "out/goku.csv")
