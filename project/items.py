from abc import ABC

from project.datatypes import Stats

class Item(ABC):
    def __init__(self, name: str, weight: int, bonus_stats: Stats):
        if not isinstance(name, str):
            raise TypeError("Il nome deve essere una stringa")
        if name == "":
            raise ValueError("Il nome non può essere una stringa vuota")
        if not isinstance(weight, int):
            raise TypeError("Il peso deve essere un intero")
        if weight < 0:
            raise ValueError("Il peso non può essere negativo")
        if not isinstance(bonus_stats, Stats):
            raise TypeError("Le statistiche bonus devono essere un'istanza di Stats")
        self.__name = name
        self.__weight = weight
        self.__bonus_stats = bonus_stats

    @property
    def name(self):
        return self.__name

    @property
    def weight(self):
        return self.__weight

    @weight.setter
    def weight(self, value: int):
        if not isinstance(value, int):
            raise TypeError("Il peso deve essere un intero")
        if value < 0:
            raise ValueError("Il peso non può essere negativo")
        self.__weight = value

    @property
    def bonus_stats(self):
        return self.__bonus_stats

    @bonus_stats.setter
    def bonus_stats(self, value: Stats):
        if not isinstance(value, Stats):
            raise TypeError("Le statistiche bonus devono essere un'istanza di Stats")
        self.__bonus_stats = value

class Weapon(Item):
    def __init__(self, name: str, weight: int, bonus_stats: Stats, damage_range: tuple[int, int], weapon_type: str, slot: str):
        super().__init__(name, weight, bonus_stats)
        if not isinstance(damage_range, tuple) or not isinstance(damage_range[0], int) or not isinstance(damage_range[1], int):
            raise TypeError("Il raggio dei danni deve essere una tupla composta da due interi")
        min_damage, max_damage = damage_range
        if min_damage > max_damage:
            raise ValueError("Il danno minimo non può essere maggiore del danno massimo")
        if min_damage < 0 or max_damage < 0:
            raise ValueError("Sia il danno minimo che il danno massimo devono essere maggiori di 0")
        if not isinstance(weapon_type, str):
            raise TypeError("Il tipo dell'arma deve essere una stringa")
        if weapon_type not in ["melee", "ranged"]:
            raise ValueError("Il tipo dell'arma deve essere o melee o ranged")
        if not isinstance(slot, str):
            raise TypeError("Lo slot dell'arma deve essere una stringa")
        if slot not in ["right hand", "left hand", "both hands"]:
            raise ValueError("L'arma può essere equipaggiata solo negli slot \"left hand\", \"right hand\", \"both hands\"")
        self.__damage_range = damage_range
        self.__weapon_type = weapon_type
        self.__slot = slot

    @property
    def damage_range(self):
        return self.__damage_range

    @damage_range.setter
    def damage_range(self, value: tuple[int, int]):
        if not isinstance(value, tuple) or not isinstance(value[0], int) or not isinstance(value[1], int):
            raise TypeError("Il raggio dei danni deve essere una tupla composta da due interi")
        min_damage, max_damage = value
        if min_damage > max_damage:
            raise ValueError("Il danno minimo non può essere maggiore del danno massimo")
        if min_damage < 0 or max_damage < 0:
            raise ValueError("Sia il danno minimo che il danno massimo devono essere maggiori di 0")
        self.__damage_range = value

    @property
    def weapon_type(self):
        return self.__weapon_type

    @property
    def slot(self):
        return self.__slot






