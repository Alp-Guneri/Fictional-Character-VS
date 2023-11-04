from character_parser import CharacterParser
from tier_parser import TierParser
from character_io import write_to_csv

if __name__ == "__main__":
    character_config_file_path = "character-config.json"
    tier_config_file_path = "tier-config.json"

    character_name = "Son Goku"

    t_parser = TierParser(tier_config_file_path)
    c_parser = CharacterParser(character_config_file_path, t_parser)

    goku = c_parser.parse_character(character_name)
    write_to_csv(goku, "out/goku.csv")
