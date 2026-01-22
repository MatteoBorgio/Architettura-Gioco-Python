from abc import ABC
from random import choice, randint

from project.characters import Character
from project.datatypes import Poison
from project.items import Item
from project.valid_slot import CHARACTER_SLOTS

class Monster(ABC):
    def __init__(self, name: str, hp: int, base_damage: int, bonus_damage: int, equipment: dict[str, Item | None], level: int):
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
        if not isinstance(level, int):
            raise TypeError("Il livello deve essere rappresentato da un intero")
        if level <= 0:
            raise ValueError("Il livello deve essere maggiore di 0")
        self.level = level
        self.__name = name
        self.__hp = hp * level
        self.__max_hp = hp
        self.__base_damage = base_damage * level
        self.__bonus_damage = bonus_damage * level
        self.__equipment = equipment

    @property
    def name(self):
        return self.__name

    @property
    def hp(self):
        return self.__hp

    @property
    def max_hp(self):
        return self.__max_hp

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

class Goblin(Monster):
    def __init__(self, name: str, hp: int, base_damage: int, bonus_damage: int, equipment: dict[str, Item], buff_stole_per_turn: int, level: int):
        super().__init__(name, hp, base_damage, bonus_damage, equipment, level)
        if not isinstance(buff_stole_per_turn, int):
            raise TypeError("Il numero di buff da rimuovere per turno deve essere rappresentato da un intero")
        if buff_stole_per_turn <= 0:
            raise ValueError("Il numero di buff da rimuovere per turno deve essere maggiore di 0")
        self.__buff_stole_per_turn = buff_stole_per_turn

    @property
    def buff_stole_per_turn(self):
        return self.__buff_stole_per_turn

    def steal(self, target: Character) -> None:
        if not isinstance(target, Character):
            raise TypeError("I buff possono essere rimossi solo da sottoclassi di Character")
        if len(target.active_buffs) <= self.buff_stole_per_turn:
            target.active_buffs = []
        else:
            for i in range(self.buff_stole_per_turn):
                random_buff_removed = choice(target.active_buffs)
                target.active_buffs.remove(random_buff_removed)

    def attack(self, target: Character) -> int:
        damage = self.base_damage
        if randint(0, 1) == 1:
            damage += self.bonus_damage
        if randint(0, 100) < 20:
            damage += self.bonus_damage
        target.receive_damage(damage)
        return damage

class Witch(Monster):
    def __init__(self, name: str, hp: int, base_damage: int, bonus_damage: int, equipment: dict[str, Item], level: int, poisons: list[Poison]):
        super().__init__(name, hp, base_damage, bonus_damage, equipment, level)
        if not isinstance(poisons, list):
            raise TypeError("I veleni devono essere rappresentati da una lista")
        for element in poisons:
            if not isinstance(element, Poison):
                raise TypeError("I veleni devono essere istanze della classe Poison")
        for poison in poisons:
            poison.damage_per_turn *= level
        self.poisons = poisons

    def cast_poison(self, poison: Poison, target: Character):
        if not isinstance(poison, Poison):
            raise TypeError("Il veleno deve essere un'istanza della classe Poison")
        if not isinstance(target, Character):
            raise TypeError("Il target deve essere un'istanza di Character o di una sua sottoclasse")
        target.add_poison(poison)
        self.poisons.remove(poison)

    def attack(self, target: Character) -> int:
        damage = self.base_damage
        if randint(0, 1) == 1:
            damage += self.bonus_damage
        if self.poisons:
            poison = choice(self.poisons)
            self.cast_poison(poison, target)
        return damage

class Zombie(Monster):
    def __init__(self, name: str, hp: int, base_damage: int, bonus_damage: int, equipment: dict[str, Item], level: int):
        super().__init__(name, hp, base_damage, bonus_damage, equipment, level)
        self.__initial_hp = hp
        self.can_revive = True

    @property
    def initial_hp(self):
        return self.__initial_hp

    def revive(self):
        if self.hp == 0 and self.can_revive:
            self.hp = self.initial_hp
            self.can_revive = False

    def receive_damage(self, damage: int) -> None:
        if not isinstance(damage, int):
            raise TypeError("Il danno deve essere un intero")
        if damage < 0:
            raise ValueError("Il danno deve essere maggiore di 0")
        self.hp = max(0, self.hp - damage)
        self.revive()

class Spider(Monster):
    def __init__(self, name: str, hp: int, base_damage: int, bonus_damage: int, equipment: dict[str, Item], level: int, poison: Poison):
        super().__init__(name, hp, base_damage, bonus_damage, equipment, level)
        if not isinstance(poison, Poison):
            raise TypeError("Il veleno deve essere un'istanza di Poison")
        poison.damage_per_turn *= level
        poison.duration *= level
        self.__poison = poison
        self.can_use_potion = True

    @property
    def poison(self):
        return self.poison

    def cast_poison(self, poison: Poison, target: Character):
        if not isinstance(poison, Poison):
            raise TypeError("Il veleno deve essere un'istanza della classe Poison")
        if not isinstance(target, Character):
            raise TypeError("Il target deve essere un'istanza di Character o di una sua sottoclasse")
        target.add_poison(poison)
        self.can_use_potion = False

    def attack(self, target: Character) -> int:
        damage = self.base_damage
        if randint(0, 1) == 1:
            damage += self.bonus_damage
        if randint(0, 100) < 40 and self.can_use_potion:
            self.cast_poison(self.poison, target)
        return damage










