import logging
import yaml
import os
from typing import Dict, Any, Optional, Union


class Config:
    _instance: Dict[str, Any] = None
    CONFIG_PATH = os.path.join(os.path.dirname(__file__), "../config.yaml")

    @classmethod
    def load_config(cls) -> Dict[str, Any]:
        if cls._instance is None:
            try:
                with open(cls.CONFIG_PATH, "r", encoding="utf-8") as file:
                    cls._instance = yaml.safe_load(file)
            except FileNotFoundError:
                logging.error("Configuration file not found.")
                cls._instance = {}
            except yaml.YAMLError as e:
                logging.error(f"Error parsing configuration file: {e}")
                cls._instance = {}
        return cls._instance


def get_user_config(qq: Union[str, int, None]) -> Dict[str, Any]:
    config = Config.load_config()
    for user in config['users']:
        if user['qq'] == qq:
            return user
    return None


def setup_logging():
    if not logging.getLogger().hasHandlers():
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(funcName)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            handlers=[
                logging.FileHandler("app.log", encoding="utf-8"),
                logging.StreamHandler(),
            ],
        )
