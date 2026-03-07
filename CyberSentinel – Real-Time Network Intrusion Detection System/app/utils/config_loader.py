"""
CyberSentinel - Configuration Loader
=====================================
Loads and parses the config.yaml file, providing a centralized
configuration dictionary for all modules in the system.
"""

import os
import yaml


# Default path to config file (relative to project root)
_DEFAULT_CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "config.yaml"
)

# Module-level cache for the loaded config
_config_cache: dict | None = None


def load_config(config_path: str | None = None) -> dict:
    """
    Load configuration from a YAML file.

    Args:
        config_path: Optional path to the config file.
                     Defaults to 'config.yaml' in the project root.

    Returns:
        Dictionary containing all configuration values.

    Raises:
        FileNotFoundError: If the config file does not exist.
        yaml.YAMLError: If the config file has invalid YAML syntax.
    """
    global _config_cache

    # Use cached config if already loaded and no custom path given
    if _config_cache is not None and config_path is None:
        return _config_cache

    # Determine the config file path
    path = config_path or _DEFAULT_CONFIG_PATH

    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Configuration file not found: {path}\n"
            f"Please ensure 'config.yaml' exists in the project root."
        )

    # Read and parse the YAML file
    with open(path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # Validate that the config is a dictionary
    if not isinstance(config, dict):
        raise ValueError(
            f"Invalid configuration format in {path}. "
            f"Expected a YAML mapping (dictionary)."
        )

    # Cache the config for future calls
    if config_path is None:
        _config_cache = config

    return config


def get_config(section: str | None = None, config_path: str | None = None) -> dict:
    """
    Get configuration values, optionally filtered by section.

    Args:
        section: Optional top-level section name (e.g., 'detection', 'dashboard').
                 If None, returns the entire config dictionary.
        config_path: Optional path to a custom config file.

    Returns:
        Configuration dictionary (full or section-specific).

    Raises:
        KeyError: If the requested section does not exist.
    """
    config = load_config(config_path)

    if section is None:
        return config

    if section not in config:
        raise KeyError(
            f"Configuration section '{section}' not found. "
            f"Available sections: {list(config.keys())}"
        )

    return config[section]


def reset_config_cache() -> None:
    """
    Reset the configuration cache.
    Useful for testing or when the config file is updated at runtime.
    """
    global _config_cache
    _config_cache = None
