from characters import Warrior, Cleric, Thief, Wizard
from datatypes import Stats, Buff
from items import Weapon
from monsters import Goblin, Spider, Witch, Zombie, Troll

class GameFactory:
        @staticmethod
        def create_character(data):
            base_stats = Stats(
                strength=data.get("strength", 0),
                dexterity=data.get("dexterity", 0),
                intelligence=data.get("intelligence", 0),
                defense=data.get("defense", 0)
            )

            sa = data.get("special_ability", {})
            special_ability = Buff(
                name=sa.get("name", ""),
                stat=sa.get("stat", ""),
                amount=sa.get("amount", 0),
                duration=sa.get("duration", 0)
            )

            cls_map = {"Warrior": Warrior, "Cleric": Cleric, "Thief": Thief, "Wizard": Wizard}
            cls = cls_map.get(data["class"])

            kwargs = {
                "name": data["name"],
                "hp": data["hp"],
                "base_stats": base_stats,
                "equipment": {"weapon": None, "armor": None},
                "mana": data.get("mana", 0),
                "mana_per_attack": data.get("mana_per_attack", 0),
                "special_ability": special_ability,
                "speed": data.get("speed", 10),
                "potions_set": data["potions_set"]
            }

            if cls is Warrior:
                kwargs["shield"] = data.get("shield", 0)
            elif cls is Cleric:
                kwargs["healing_per_attack"] = data.get("healing_per_attack", 0)
                kwargs["poisons_mitigation"] = data.get("poison_mitigation", 0)
            elif cls is Thief:
                kwargs["critical_bonus"] = data.get("critical_bonus", 0)
            elif cls is Wizard:
                kwargs["buff_amount_boost"] = data.get("buff_amount_boost", 0)
                kwargs["buff_duration_boost"] = data.get("buff_duration_boost", 0)

            return cls(**kwargs)

        @staticmethod
        def create_weapon(data):
            base_stats = Stats(
                strength=data.get("strength", 0),
                dexterity=data.get("dexterity", 0),
                intelligence=data.get("intelligence", 0),
                defense=data.get("defense", 0)
            )
            return Weapon(
                name=data["name"],
                weight=int(data["weight"]),
                bonus_stats=base_stats,
                damage_range=(data["damage_range_min"], data["damage_range_max"]),
                weapon_type=data["weapon_type"],
                slot=data["slot"]
            )

        @staticmethod
        def create_monster(data):
            cls_map = {"Goblin": Goblin, "Witch": Witch, "Spider": Spider, "Zombie": Zombie, "Troll": Troll}
            cls = cls_map.get(data["class"])

            kwargs = {
                "name": data["name"],
                "hp": data["hp"],
                "base_damage": data["base_damage"],
                "bonus_damage": data["bonus_damage"],
                "speed": data["speed"],
                "equipment": {"weapon": None, "armor": None},
                "level": 1
            }

            if cls is Goblin:
                kwargs["buff_stole_per_turn"] = data["buff_stole_per_turn"]
            elif cls is Troll:
                kwargs["brute_force"] = data["brute_force"]

            return cls(**kwargs)
