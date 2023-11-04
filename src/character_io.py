import csv
import os

from . import DEFAULT_OUTPUT_DIR
from src.character import FictionalCharacter, FictionalCharacterVersion
from src.tier import TierClassifier


def write_to_csv(character: FictionalCharacter, output_file_path: str = None):
    file_name = character.character_name.strip().replace(" ", "-")
    if output_file_path is None:
        output_file_path = f"{DEFAULT_OUTPUT_DIR}/{file_name}.csv"
    directory = os.path.dirname(output_file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

    # The names of the stats associated with the character
    stat_names = list(character.character_versions[0].stat_tier_map.keys())

    # Prepare the data for writing to the CSV file
    data = []

    # Add the legend in the first row
    legend = ["Character Version"] + stat_names
    data.append(legend)

    # Loop through character versions and add data for each version
    for version in character.character_versions:
        version_data = [version.version_name]
        for stat_name in stat_names:
            version_data.append(version.stat_tier_map[stat_name].default_tier_name)
        data.append(version_data)

    # Write the data to a CSV file
    with open(output_file_path, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerows(data)


def read_from_csv(character_name: str, tier_classifier: TierClassifier, input_file_path: str = None):
    default_file_name = character_name.strip().replace(" ", "-")
    if input_file_path is None:
        input_file_path = f"{DEFAULT_OUTPUT_DIR}/{default_file_name}.csv"

    with open(input_file_path, mode='r') as file:
        reader = csv.reader(file)
        legend = next(reader)

        character_versions = []
        for row in reader:
            version_name = row[0]
            version_stats = {}
            for i in range(1, len(row)):
                stat_name = legend[i]
                tier_value = tier_classifier.get_tier_from_name(stat_name, row[i])
                version_stats[stat_name] = tier_value
            character_version = FictionalCharacterVersion(version_name, version_stats)
            character_versions.append(character_version)

    return FictionalCharacter(character_name, character_versions)
