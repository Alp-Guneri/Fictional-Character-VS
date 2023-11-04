import csv
import os

from character import FictionalCharacter


def write_to_csv(character: FictionalCharacter, output_file_path: str = None):
    file_name = character.character_name.strip().replace(" ", "-")
    if output_file_path is None:
        output_file_path = f"out/{file_name}.csv"
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
