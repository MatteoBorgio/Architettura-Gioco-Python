from abc import ABC, abstractmethod
from random import randint

from project.datatypes import Stats, Buff
from project.errors import InvalidEquipError
from project.items import Item
from project.valid_slot import CHARACTER_SLOTS

class Character(ABC):
    def __init__(self, name: str, hp: int, base_stats: Stats, equipment: dict[str, Item | None], mana: int):
        if not isinstance(name, str):
            raise TypeError("Il nome deve essere una stringa")
        if name == "":
            raise ValueError("Il nome non può essere una stringa vuota")
        if not isinstance(hp, int):
            raise TypeError("La vita deve essere rappresentata da un intero")
        if hp <= 0:
            raise TypeError("La vita deve essere inizializzata maggiore di 0")
        if not isinstance(base_stats, Stats):
            raise TypeError("Le statistiche base devono essere un'istanza di Stats")
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
        self.__special_ability = None

    @property
    def name(self):
        return self.__name

    @property
    def hp(self):
        return self.__hp

    @hp.setter
    def hp(self, value: int | float):
        if not isinstance(value, int) and not isinstance(value, float):
            raise TypeError("La vita deve essere rappresentata da un intero o da un numero decimale")
        if value < 0:
            raise ValueError("La vita non può essere negativa")
        self.__hp = value

    @property
    def special_ability(self):
        return self.__special_ability

    @property
    def base_stats(self):
        return self.__base_stats

    @base_stats.setter
    def base_stats(self, value: Stats):
        if not isinstance(value, Stats):
            raise TypeError("Le statistiche base devono essere un'istanza di Stats")
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
        self.__base_stats = self.base_stats + item.bonus_stats

    def unequip(self, item: Item) -> None:
        if not isinstance(item, Item):
            raise TypeError("L'oggetto da disequipaggiare deve essere un'istanza di una sottoclasse di Item")
        if self.equipment[item.slot] != item:
            raise ValueError("L'oggetto da disequipaggiare non è nell'quipaggiamento del personaggio")
        self.__equipment[item.slot] = None
        self.__base_stats = self.base_stats - item.bonus_stats

    def receive_damage(self, damage: float) -> None:
        if not isinstance(damage, float):
            raise TypeError("Il danno deve essere un numero decimale (float)")
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

    def apply_buffs(self, buffs: list[Buff]):
        if not isinstance(buffs, list):
            raise TypeError("I buff devono essere rappresentati da una lista")
        for element in buffs:
            if not isinstance(element, Buff):
                raise TypeError("Tutti i buff devono essere un'istanza di Buff")
        for buff in buffs:
            setattr(self.__base_stats, buff.stat,(getattr(self.__base_stats, buff.stat) + buff.amount))

    def remove_buffs(self, buffs: list[Buff]):
        if not isinstance(buffs, list):
            raise TypeError("I buff devono essere rappresentati da una lista")
        for element in buffs:
            if not isinstance(element, Buff):
                raise TypeError("Tutti i buff devono essere un'istanza di Buff")
        for buff in buffs:
            if buff.duration == 0:
                setattr(self.__base_stats, buff.stat, (getattr(self.__base_stats, buff.stat) - buff.amount))
                self.__active_buffs.remove(buff)

    def use_special_ability(self):
        self.add_buff(self.__special_ability)

    @staticmethod
    def tick_buffs(buffs: list[Buff]):
        if not isinstance(buffs, list):
            raise TypeError("I buff devono essere rappresentati da una lista")
        for element in buffs:
            if not isinstance(element, Buff):
                raise TypeError("Tutti i buff devono essere un'istanza di Buff")
        for buff in buffs:
            buff.duration -= 1

    @abstractmethod
    def attack(self, target: "Character"):
        pass

    def __str__(self):
        return f"{self.name} ({self.hp}/{self.max_hp})"

class Warrior(Character):
    def __init__(self, name: str, hp: int, base_stats: Stats, equipment: dict[str, Item | None], mana: int, damage_bonus: tuple[int, int]):
        super().__init__(name, hp, base_stats, equipment, mana)
        if not isinstance(damage_bonus, tuple):
            raise TypeError("I danni aggiuntivi devono essere rappresentati da un intero")
        min_damage, max_damage = damage_bonus
        if not isinstance(min_damage, int) or not isinstance(max_damage, int):
            raise TypeError("I danni aggiuntivi devono essere rappresentati da una tupla contentente due interi")
        if min_damage > max_damage:
            raise ValueError("Il danno minimo non può essere maggiore del danno massimo")
        self.__damage_bonus = damage_bonus
        self.__special_ability = Buff("Warrior's Might", "strength", 5, 3)

    @property
    def damage_bonus(self):
        return self.__damage_bonus

    def attack(self, target: "Character") -> None:
        damage = (self.base_stats.strength * 0.5) + (self.base_stats.dexterity * 0.3) + (self.base_stats.intelligence * 0.2) + randint(self.damage_bonus[0], self.damage_bonus[1])
        target.receive_damage(damage)