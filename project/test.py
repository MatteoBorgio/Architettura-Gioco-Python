from project.characters import Warrior
from project.datatypes import Stats
from project.items import Weapon

if __name__ == "__main__":
    char1 = Warrior("Jon Snow", 100, Stats(10, 2, 5, 3), {"head": None,
                                                          "chest": None,
                                                          "legs": None,
                                                          "feet": None,
                                                          "hands": None,
                                                          "shoulder": None,
                                                          "weapon": None}, 10, (5, 10))
    print(char1)
    print(char1.base_stats)
    char1.equip(Weapon("Axe", 100, Stats(5, 0, 1, 0), (5, 10), "melee", "weapon"))
    print(char1.base_stats)
    for k, v in char1.equipment.items():
        print(v)
