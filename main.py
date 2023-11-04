from src.character_parser import CharacterParser
from src.tier import TierClassifier
from src.tier_parser import TierParser
from src.character_io import write_to_csv, read_from_csv
from src.battle import versus_battle

if __name__ == "__main__":
    first_character_name = "Son Goku"
    second_character_name = "Saitama"

    t_classifier = TierClassifier()

    goku = read_from_csv(first_character_name, t_classifier)
    saitama = read_from_csv(second_character_name, t_classifier)

    goku_ultra_instinct = next(element for element in goku.character_versions
                               if "Perfected Ultra Instinct" in element.version_name)

    saitama_parallel_timeline = next(element for element in saitama.character_versions
                                     if "Parallel Timeline" in element.version_name)

    print(versus_battle(goku_ultra_instinct, saitama_parallel_timeline))

    # character_name = "Saitama"
    # t_classifier = TierClassifier()
    # t_parser = TierParser(t_classifier)
    # c_parser = CharacterParser(t_parser)
    #
    # saitama = c_parser.parse_character(character_name)
    # write_to_csv(saitama)
