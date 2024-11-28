import json
import os
from hermes.exceptions import HermesException, ConfigurationError

DEFAULT_CONFIG = {
    "debug": False,
    "console_log": False,
    "database_path": "hermes.db",
    "migrations_dir": "migrations"
}

CONFIG_PATH = "hermes_config.json"

def get_config():
    """
    Load configuration from a JSON file. If the file does not exist,
    default settings are used, and the file is created.

    Returns:
        dict: The configuration settings.
    """
    try:
        if not os.path.exists(CONFIG_PATH):
            create_default_config()
            if DEFAULT_CONFIG.get("console_log", True):
                print(f"Default configuration created at '{CONFIG_PATH}'.")
        with open(CONFIG_PATH, "r") as file:
            config = json.load(file)

        # Merge environment variables
        config["database_path"] = os.getenv("HERMES_DATABASE_PATH", config["database_path"])
        config["migrations_dir"] = os.getenv("HERMES_MIGRATIONS_DIR", config["migrations_dir"])
        config["debug"] = os.getenv("HERMES_DEBUG", str(config.get("debug", False))).lower() == 'true'
        config["console_log"] = os.getenv("HERMES_CONSOLE_LOG", str(config.get("console_log", True))).lower() == 'true'

        validate_config(config)
        return config
    except Exception as e:
        raise ConfigurationError(f"Failed to load configuration: {e}")

def create_default_config():
    """
    Create a default configuration file.
    """
    try:
        with open(CONFIG_PATH, "w") as file:
            json.dump(DEFAULT_CONFIG, file, indent=4)
    except Exception as e:
        raise ConfigurationError(f"Failed to create default configuration: {e}")

def update_config(new_config):
    """
    Update the configuration file with new settings.

    Args:
        new_config (dict): Dictionary of configuration settings to update.
    """
    try:
        config = get_config()
        config.update(new_config)
        with open(CONFIG_PATH, "w") as file:
            json.dump(config, file, indent=4)
        if config.get("console_log", True):
            print("Configuration updated successfully.")
    except Exception as e:
        raise ConfigurationError(f"Failed to update configuration: {e}")

def validate_config(config):
    """
    Validate the configuration settings.

    Args:
        config (dict): The configuration settings.

    Raises:
        ConfigurationError: If required settings are missing or invalid.
    """
    required_keys = ["database_path", "migrations_dir", "debug", "console_log"]
    for key in required_keys:
        if key not in config:
            raise ConfigurationError(f"The '{key}' configuration is required.")
    if not isinstance(config["debug"], bool):
        raise ConfigurationError("The 'debug' configuration must be a boolean.")
    if not isinstance(config["console_log"], bool):
        raise ConfigurationError("The 'console_log' configuration must be a boolean.")
    if not config["database_path"]:
        raise ConfigurationError("The 'database_path' cannot be empty.")
    if not config["migrations_dir"]:
        raise ConfigurationError("The 'migrations_dir' cannot be empty.")
