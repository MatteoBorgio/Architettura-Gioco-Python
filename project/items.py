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

