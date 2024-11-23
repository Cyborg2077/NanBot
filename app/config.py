import logging
import yaml

CONFIG = None


def load_config():
    global CONFIG
    if CONFIG is None:  # 确保只加载一次
        with open(r"../config.yaml", "r", encoding="utf-8") as file:
            CONFIG = yaml.safe_load(file)
    return CONFIG


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(funcName)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.FileHandler("app.log", encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )
