from abc import ABC
from random import choice, randint

from project.characters import Character
from project.items import Item
from project.valid_slot import CHARACTER_SLOTS

class Monster(ABC):
    def __init__(self, name: str, hp: int, base_damage: int, bonus_damage: int, equipment: dict[str, Item | None]):
        if not isinstance(name, str):
            raise TypeError("Il nome deve essere una stringa")
        if name == "":
            raise ValueError("Il nome non può essere una stringa vuota")
        if not isinstance(hp, int):
            raise TypeError("I punti vita devono essere rappresentati da un intero")
        if hp <= 0:
            raise ValueError("I punti vita devono essere inizializzati maggiori di 0")
        if not isinstance(base_damage, int):
            raise TypeError("I danni base devono essere rappresentati da un intero")
        if base_damage <= 0:
            raise ValueError("I danni base devono essere maggiori di 0")
        if not isinstance(bonus_damage, int):
            raise TypeError("I danni bonus devono essere rappresentati da un intero")
        if bonus_damage <= 0:
            raise ValueError("I danni bonus devono essere maggiori di 0")
        if not isinstance(equipment, dict):
            raise TypeError("L'equipaggiamento deve essere un dizionario")
        for k, v in equipment.items():
            if k not in CHARACTER_SLOTS:
                raise ValueError(f"Gli oggetti possono essere equipaggiati solo in questi slot: {CHARACTER_SLOTS}")
            if not isinstance(v, Item) and v is not None:
                raise ValueError("Gli unici oggetti validi da poter equipaggiare sono le istanze di Item o le sue sottoclassi")
        self.__name = name
        self.__hp = hp
        self.__base_damage = base_damage
        self.__bonus_damage = bonus_damage
        self.__equipment = equipment

    @property
    def name(self):
        return self.__name

    @property
    def hp(self):
        return self.__hp

    @hp.setter
    def hp(self, value: int):
        if not isinstance(value, int):
            raise TypeError("I punti vita devono essere rappresentati da un intero")
        if value < 0:
            raise ValueError("I punti vita non possono essere negativi")
        self.__hp = value

    @property
    def base_damage(self):
        return self.__base_damage

    @property
    def bonus_damage(self):
        return self.__bonus_damage

    @property
    def equipment(self):
        return self.__equipment

    def receive_damage(self, damage: int) -> None:
        if not isinstance(damage, int):
            raise TypeError("Il danno deve essere un intero")
        if damage < 0:
            raise ValueError("Il danno deve essere maggiore di 0")
        self.hp = max(0, self.hp - damage)

    @staticmethod
    def drop_item(items: dict[str, Item | None]) -> Item | None:
        possible_drop = []
        for v in items.values():
            if v is not None:
                possible_drop.append(v)
        if not possible_drop:
            return None
        else:
            return choice(possible_drop)

    def attack(self, target: Character) -> int:
        damage = self.base_damage
        if randint(0, 1) == 1:
            damage += self.bonus_damage
        target.receive_damage(damage)
        return damage



