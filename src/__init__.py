import os

# Get the absolute path of the current file (__init__.py)
current_file = __file__

# Determine the parent directory of the current file (src directory)
SRC_DIR = os.path.dirname(current_file)

# Determine the parent directory of the src directory (project root)
PROJECT_DIR = os.path.dirname(SRC_DIR)

# Determine the default config directory
CONFIG_DIR = os.path.join(PROJECT_DIR, 'config')

# Determine the default output directory
DEFAULT_OUTPUT_DIR = os.path.join(PROJECT_DIR, 'out')

DEFAULT_CHARACTER_CONFIG_PATH = os.path.join(CONFIG_DIR, 'character-config.json')
DEFAULT_TIER_CONFIG_PATH = os.path.join(CONFIG_DIR, 'tier-config.json')
