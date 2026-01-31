import json
import random
from project.assets_manager import AssetsManager
from project.factory import GameFactory

class DataManager:
    DATA_FILES = {
        "characters": ("data", "characters.json"),
        "weapons": ("data", "weapons.json"),
        "projectiles": ("data", "projectiles.json"),
        "monsters": ("data", "monsters.json")
    }

    _raw_monsters = []
    _projectiles = []

    @staticmethod
    def _load_json(key):
        path = AssetsManager.asset_path("..", *DataManager.DATA_FILES[key])
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def load_data():
        raw_chars = DataManager._load_json("characters")
        raw_weapons = DataManager._load_json("weapons")
        DataManager._raw_monsters = DataManager._load_json("monsters")
        DataManager._projectiles = DataManager._load_json("projectiles")

        weapons = [GameFactory.create_weapon(d) for d in raw_weapons]
        weapon_map = {w.name: w for w in weapons}

        characters = []
        for d in raw_chars:
            char = GameFactory.create_character(d)
            weapon_name = d.get("default_weapon")
            if weapon_name in weapon_map:
                char.equip(weapon_map[weapon_name])
            characters.append(char)

        return characters, weapons

    @staticmethod
    def get_random_monster():
        if not DataManager._raw_monsters:
            return None

        data = random.choice(DataManager._raw_monsters)
        return GameFactory.create_monster(data)

    @staticmethod
    def get_projectile_data(weapon_name):
        for p in DataManager._projectiles:
            if p["weapon"] == weapon_name:
                return {
                    "name": p["projectile_type"],
                    "speed": p["speed"],
                    "effect": p["effect"]
                }
        return None