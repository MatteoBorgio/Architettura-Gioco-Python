from abc import ABC, abstractmethod

from project.datatypes import Stats, Buff
from project.errors import InvalidEquipError
from project.items import Item
from project.valid_slot import CHARACTER_SLOTS

class Character(ABC):
    def __init__(self, name: str, hp: int, base_stats: Stats, equipment: dict[str, Item | None], mana: int):
        if not isinstance(name, int):
            TypeError("Il nome deve essere una stringa")
        if name == "":
            ValueError("Il nome non può essere una stringa vuota")
        if not isinstance(hp, int):
            TypeError("La vita deve essere rappresentata da un intero")
        if hp <= 0:
            TypeError("La vita deve essere inizializzata maggiore di 0")
        if not isinstance(base_stats, Stats):
            TypeError("Le statistiche base devono essere un'istanza di Stats")
        if not isinstance(equipment, dict):
            raise TypeError("L'equipaggiamento deve essere un dizionario")
        for k, v in equipment.items():
            if k not in CHARACTER_SLOTS:
                raise ValueError(f"Gli oggetti possono essere equipaggiati solo in questi slot: {CHARACTER_SLOTS}")
            if not isinstance(v, Item) and v is not None:
                raise ValueError("Gli unici oggetti validi da poter equipaggiare sono le istanze di Item o le sue sottoclassi")
        if not isinstance(mana, int):
           raise TypeError("Il mana deve essere rappresentato da un intero")
        if mana <= 0:
            raise ValueError("Il mana deve essere inizializzato maggiore di 0")
        self.__name = name
        self.__hp = hp
        self.__base_stats = base_stats
        self.__equipment = equipment
        self.__mana = mana
        self.__max_hp = hp
        self.__active_buffs = []

    @property
    def name(self):
        return self.__name

    @property
    def hp(self):
        return self.__hp

    @hp.setter
    def hp(self, value: int):
        if not isinstance(value, int):
            TypeError("La vita deve essere rappresentata da un intero")
        if value < 0:
            ValueError("La vita non può essere negativa")
        self.__hp = value

    @property
    def base_stats(self):
        return self.__base_stats

    @base_stats.setter
    def base_stats(self, value: Stats):
        if not isinstance(value, Stats):
            TypeError("Le statistiche base devono essere un'istanza di Stats")
        self.__base_stats = value

    @property
    def equipment(self):
        return self.__equipment

    @property
    def mana(self):
        return self.__mana

    @mana.setter
    def mana(self, value: int):
        if not isinstance(value, int):
            raise TypeError("Il mana deve essere rappresentato da un intero")
        if value < 0:
            raise ValueError("Il mana non può essere negativo")
        self.__mana = value

    @property
    def max_hp(self):
        return self.__max_hp

    @property
    def active_buffs(self):
        return self.__active_buffs

    def equip(self, item: Item) -> None:
        if not isinstance(item, Item):
            raise TypeError("L'oggetto da equipaggiare deve essere un'istanza di una sottoclasse di Item")
        if self.__equipment[item.slot] is not None:
            raise InvalidEquipError
        self.__equipment[item.slot] = item

    def unequip(self, item: Item) -> None:
        if not isinstance(item, Item):
            raise TypeError("L'oggetto da disequipaggiare deve essere un'istanza di una sottoclasse di Item")
        if self.equipment[item.slot] != item:
            raise ValueError("L'oggetto da disequipaggiare non è nell'quipaggiamento del personaggio")
        self.__equipment[item.slot] = None

    def receive_damage(self, damage: int) -> None:
        if not isinstance(damage, int):
            raise TypeError("Il danno deve essere un intero")
        if damage < 0:
            raise ValueError("Il danno deve essere maggiore di 0")
        self.hp = max(0, (self.hp - damage))

    def is_alive(self) -> bool:
        if self.__hp > 0:
            return True
        else:
            return False

    def heal(self, amount: int) -> None:
        if not isinstance(amount, int):
            raise TypeError("La quantità di hp curati deve essere rappresentata da un intero")
        if amount == 0:
            raise ValueError("La quantità di hp curati non può essere negativa")
        self.hp = min(self.max_hp, (self.hp + amount))

    def add_buff(self, buff: Buff) -> None:
        if not isinstance(buff, Buff):
            raise TypeError("Un buff deve essere un'istanza di Buff")
        self.__active_buffs.append(buff)

    @abstractmethod
    def attack(self, target: "Character"):
        pass

    @abstractmethod
    def use_special_ability(self, target: "Character"):
        pass

