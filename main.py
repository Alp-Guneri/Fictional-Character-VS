from character_parser import CharacterParser
from tier_parser import TierParser

if __name__ == "__main__":
    character_config_file_path = "character-config.json"
    tier_config_file_path = "tier-config.json"

    character_name = "Son Goku"

    t_parser = TierParser(tier_config_file_path)
    c_parser = CharacterParser(character_config_file_path, character_name, t_parser)
    c_parser.parse_and_write()
