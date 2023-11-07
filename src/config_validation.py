import json

from . import DEFAULT_TIER_CONFIG_SCHEMA_PATH, DEFAULT_CHARACTER_CONFIG_SCHEMA_PATH
from jsonschema import validate, ValidationError


def validate_character_schema(character_config_json):
    try:
        with open(DEFAULT_CHARACTER_CONFIG_SCHEMA_PATH, 'r') as config_file:
            schema = json.load(config_file)
            validate(character_config_json, schema)
    except FileNotFoundError:
        raise FileNotFoundError(f"Character config schema file not found: {DEFAULT_CHARACTER_CONFIG_SCHEMA_PATH}")
    except ValidationError:
        raise


def validate_tier_schema(tier_config_json):
    try:
        with open(DEFAULT_TIER_CONFIG_SCHEMA_PATH, 'r') as config_file:
            schema = json.load(config_file)
            validate(tier_config_json, schema)
            tier_schema = schema["properties"]["tier"]
            stat_names = tier_config_json["statNames"]
            for stat_name in stat_names:
                if stat_name in tier_config_json:
                    validate(tier_config_json[stat_name], tier_schema)
    except FileNotFoundError:
        raise FileNotFoundError(f"Tier config schema file not found: {DEFAULT_CHARACTER_CONFIG_SCHEMA_PATH}")
    except ValidationError:
        raise
