import os
import json
import logging

_logger = logging.getLogger(__name__)

DEFAULT_CONFIG = {
    'watch_directories': [],
    'data_dir': os.path.join(os.path.expanduser('~'), '.pixeltext_data'),
    'valid_extensions': ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff'],
    'log_level': 'INFO'
}

CONFIG_FILE = os.path.join(os.path.expanduser('~'), '.pixeltext.json')

def load_config():
    """Loads the configuration from the config file, or creates a default one if it doesn't exist."""
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
        # Merge with default config to ensure all keys are present
        config = {**DEFAULT_CONFIG, **config}
        _logger.info(f"Configuration loaded from {CONFIG_FILE}")
    except FileNotFoundError:
        _logger.warning("Config file not found. Creating default config.")
        config = DEFAULT_CONFIG
        save_config(config)
    except json.JSONDecodeError:
        _logger.error(f"Error decoding JSON from {CONFIG_FILE}. Loading default config.")
        config = DEFAULT_CONFIG
    return config

def save_config(config):
    """Saves the configuration to the config file."""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)
    _logger.info(f"Configuration saved to {CONFIG_FILE}")

def get_config_value(key):
    """Gets a specific value from the configuration."""
    config = load_config()
    return config.get(key)

def set_config_value(key, value):
    """Sets a specific value in the configuration and saves the config."""
    config = load_config()
    config[key] = value
    save_config(config)
