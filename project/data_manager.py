import json
from project.assets_manager import AssetsManager
from project.factory import GameFactory

class DataManager:
    DATA_FILES = {
        "characters": ("data", "characters.json"),
        "weapons": ("data", "weapons.json"),
        "projectiles": ("data", "projectiles.json"),
        "monsters": ("data", "monsters.json")
    }

    @staticmethod
    def _load_json(key):
        path = AssetsManager.asset_path("..", *DataManager.DATA_FILES[key])
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def load_data():
        raw_chars = DataManager._load_json("characters")
        raw_weapons = DataManager._load_json("weapons")
        raw_monsters = DataManager._load_json("monsters")
        projectiles = DataManager._load_json("projectiles")

        weapons = [GameFactory.create_weapon(d) for d in raw_weapons]
        monsters = [GameFactory.create_monster(d) for d in raw_monsters]

        weapon_map = {w.name: w for w in weapons}

        characters = []
        for d in raw_chars:
            char = GameFactory.create_character(d)
            weapon_name = d.get("default_weapon")
            if weapon_name in weapon_map:
                char.equip(weapon_map[weapon_name])

            characters.append(char)

        return characters, weapons, projectiles, monsters