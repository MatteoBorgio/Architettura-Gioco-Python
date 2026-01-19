from abc import ABC, abstractmethod
from random import randint
from typing import override

from project.datatypes import Stats, Buff, Poison
from project.errors import InvalidEquipError
from project.items import Item
from project.potions import Potion
from project.valid_slot import CHARACTER_SLOTS

class Character(ABC):
    def __init__(self, name: str, hp: int, base_stats: Stats, equipment: dict[str, Item | None], mana: int, mana_per_attack: int, special_ability: Buff, potions_set: list[Potion]):
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
        if not isinstance(mana_per_attack, int):
            raise TypeError("Il mana consumato per ogni attacco deve essere un intero")
        if mana_per_attack <= 0:
            raise ValueError("Il mana consumato per ogni attacco deve essere maggiore di 0")
        if not isinstance(special_ability, Buff):
            raise TypeError("L'abilità speciale deve essere un'istanza di buff")
        if not isinstance(potions_set, list):
            raise TypeError("Il set di pozioni deve essere rappresentato da una lista")
        for element in potions_set:
            if not isinstance(element, Potion):
                raise TypeError("Il set di pozioni deve essere composto da sottoclassi di Potion")

        self.__name = name
        self.__hp = hp
        self.__base_stats = base_stats
        self.__equipment = equipment
        self.__mana = mana
        self.__max_hp = hp
        self.__active_buffs = []
        self.__special_ability = special_ability
        self.__mana_per_attack = mana_per_attack
        self.__special_ability_used = False
        self.__potions_set = potions_set
        self.active_poisons = []

    @property
    def name(self):
        return self.__name

    @property
    def hp(self):
        return self.__hp

    @hp.setter
    def hp(self, value: int):
        if not isinstance(value, int):
            raise TypeError("La vita deve essere rappresentata da un intero")
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
    def used_special_ability(self):
        return self.__special_ability_used

    @used_special_ability.setter
    def used_special_ability(self, value: bool):
        if not isinstance(value, bool):
            raise TypeError("Lo stato di utilizzo dell'abilità speciale deve essere un booleano")
        self.__special_ability_used = value

    @property
    def equipment(self):
        return self.__equipment

    @property
    def mana(self):
        return self.__mana

    @property
    def mana_per_attack(self):
        return self.__mana_per_attack

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

    @property
    def potions_set(self):
        return self.__potions_set

    @property
    def show_potions(self):
        return "{" + ", ".join(str(p) for p in self.__potions_set) + "}"

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

    def receive_damage(self, damage: int) -> None:
        if not isinstance(damage, int):
            raise TypeError("Il danno deve essere un intero")
        if damage < 0:
            raise ValueError("Il danno deve essere maggiore di 0")
        self.hp = max(0, int(self.hp - (damage - (self.base_stats.defense * 0.3))))

    def is_alive(self) -> bool:
        if self.__hp > 0:
            return True
        else:
            return False

    def heal(self, amount: int) -> None:
        if not isinstance(amount, int):
            raise TypeError("La quantità di hp curati deve essere rappresentata da un intero")
        if amount < 0:
            raise ValueError("La quantità di hp curati non può essere negativa")
        self.hp = min(self.max_hp, (self.hp + amount))

    def recharge(self, amount: int) -> None:
        if not isinstance(amount, int):
            raise TypeError("La quantità di mana da ricaricare deve essere rappresentata da un intero")
        if amount < 0:
            raise ValueError("La quantità di mana da ricaricare non può essere negativa")
        self.mana += amount

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

    def add_poison(self, poison: Poison):
        if not isinstance(poison, Poison):
            raise TypeError("Un veleno deve essere un'istanza di Poison")
        self.active_poisons.append(poison)

    def apply_poisons(self, poisons: list[Poison]):
        if not isinstance(poisons, list):
            raise TypeError("I veleni devono essere rappresentati da una lista")
        for element in poisons:
            if not isinstance(element, Poison):
                raise TypeError("Tutti i veleni devono essere istanze di Poison")
        for poison in poisons:
            self.hp = max(0, self.hp - poison.damage_per_turn)

    def remove_poisons(self, poisons: list[Poison]):
        if not isinstance(poisons, list):
            raise TypeError("I veleni devono essere rappresentati da una lista")
        for element in poisons:
            if not isinstance(element, Poison):
                raise TypeError("Tutti i veleni devono essere un'istanza di Poison")
        for poison in poisons:
            if poison.duration == 0:
                self.active_poisons.remove(poison)

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

    @staticmethod
    def tick_potion(potions: list[Potion]):
        if not isinstance(potions, list):
            raise TypeError("Il set di pozioni deve essere una lista")
        for element in potions:
            if not isinstance(element, Potion):
                raise TypeError("Gli elementi nel set di pozioni devono essere tutte istanze di sottoclassi di Potion")
        for potion in potions:
            if potion.uses == 0:
                potions.remove(potion)

    @abstractmethod
    def attack(self, target: "Character") -> int:
        pass

    def __str__(self):
        return f"{self.name} ({self.hp}/{self.max_hp})"

class Warrior(Character):
    def __init__(self, name: str, hp: int, base_stats: Stats, equipment: dict[str, Item | None], mana: int, mana_per_attack: int, special_ability: Buff, potions_set: list[Potion], shield: int):
        super().__init__(name, hp, base_stats, equipment, mana, mana_per_attack, special_ability, potions_set)
        if not isinstance(shield, int):
            raise TypeError("Lo scudo deve essere rappresentato da un intero")
        if shield <= 0:
            raise ValueError("Lo scudo deve essere maggiore di 0")
        self.__shield = shield

    @property
    def shield(self):
        return self.__shield

    @override
    def receive_damage(self, damage: int) -> None:
        if not isinstance(damage, int):
            raise TypeError("Il danno deve essere un intero")
        if damage < 0:
            raise ValueError("Il danno deve essere maggiore di 0")
        self.hp = max(0, int(self.hp - (damage - (self.base_stats.defense * 0.3) - self.shield)))

    def attack(self, target: "Character") -> int:
        if (self.mana - self.mana_per_attack) >= 0:
            damage_dealt = int((self.base_stats.strength * 0.5) + (self.base_stats.dexterity * 0.3) + (self.base_stats.intelligence * 0.2))
            target.receive_damage(damage_dealt)
            self.mana -= self.mana_per_attack
            return damage_dealt
        else:
            return 0

class Cleric(Character):
    def __init__(self, name: str, hp: int, base_stats: Stats, equipment: dict[str, Item | None], mana: int, mana_per_attack: int, special_ability: Buff, potions_set: list[Potion], poisons_mitigation: int, healing_per_attack: int):
        super().__init__(name, hp, base_stats, equipment, mana, mana_per_attack, special_ability, potions_set)
        if not isinstance(poisons_mitigation, int):
            raise TypeError("La mitigazione dei veleni deve essere rappresentata da un intero")
        if poisons_mitigation <= 0:
            raise ValueError("La mitigazione dei veleni deve essere maggiore di 0")
        if not isinstance(healing_per_attack, int):
            raise TypeError("I danni recuperati dopo un attacco devono essere rappresentati da un intero")
        if healing_per_attack <= 0:
            raise ValueError("I danni recuperati dopo un attacco devono essere maggiori di 0")
        self.__poisons_mitigation = poisons_mitigation
        self.__healing_per_attack = healing_per_attack

    @property
    def poisons_mitigation(self):
        return self.__poisons_mitigation

    @property
    def healing_per_attack(self):
        return self.__healing_per_attack

    def mitigate_poisons(self) -> None:
        for poison in self.active_poisons:
            poison.damage_per_turn = max(0, poison.damage_per_turn - self.poisons_mitigation)

    def attack(self, target: "Character") -> int:
        if (self.mana - self.mana_per_attack) >= 0:
            damage_dealt = int((self.base_stats.strength * 0.3) + (self.base_stats.dexterity * 0.3) + (self.base_stats.intelligence * 0.4))
            target.receive_damage(damage_dealt)
            self.mana -= self.mana_per_attack
            self.heal(self.healing_per_attack)
            return damage_dealt
        else:
            return 0

class Thief(Character):
    def __init__(self, name: str, hp: int, base_stats: Stats, equipment: dict[str, Item | None], mana: int, mana_per_attack: int, special_ability: Buff, potions_set: list[Potion], critical_bonus: int):
        super().__init__(name, hp, base_stats, equipment, mana, mana_per_attack, special_ability, potions_set)
        if not isinstance(critical_bonus, int):
            raise TypeError("I danni critici devono essere rappresentati da un intero")
        if critical_bonus <= 0:
            raise ValueError("I danni critici devono essere rappresentati da un intero")
        self.__critical_bonus = critical_bonus

    @property
    def critical_bonus(self):
        return self.__critical_bonus

    def attack(self, target: "Character") -> int:
        if (self.mana - self.mana_per_attack) >= 0:
            damage_dealt = int((self.base_stats.strength * 0.1) + (self.base_stats.dexterity * 0.4) + (self.base_stats.intelligence * 0.5))
            if randint(0, 1) == 1:
                damage_dealt += self.critical_bonus
            return damage_dealt
        else:
            return 0

