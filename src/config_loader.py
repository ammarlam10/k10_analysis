# project_root/src/config_loader.py

import yaml
import os
import logging

logger = logging.getLogger(__name__)

def load_config(config_path="./config/config.yaml"):
    """
    Loads configuration from a YAML file.

    Args:
        config_path (str): The path to the YAML configuration file.

    Returns:
        dict: A dictionary containing the configuration parameters.

    Raises:
        FileNotFoundError: If the config file does not exist.
        yaml.YAMLError: If there is an error parsing the YAML file.
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(config_path, 'r') as f:
        try:
            config = yaml.safe_load(f)
            return config
        except yaml.YAMLError as e:
            raise  # Re-raise the exception after logging

