import json
import os

def load_config():
    # Automatically resolves the path relative to this file's location
    config_path = os.path.join(os.path.dirname(__file__), "config", "config.json")
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)

CONFIG = load_config()
CURRENT_LANG = CONFIG["settings"]["default_language"]