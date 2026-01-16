from abc import abstractmethod

from project.characters import Character
from project.datatypes import Buff

class Potion:
    def __init__(self, name: str, mana_consume: int, uses=1):
        if not isinstance(name, str):
            raise TypeError("Il nome deve essere una stringa")
        if name == "":
            raise ValueError("Il nome non può essere una stringa vuota")
        if not isinstance(mana_consume, int):
            raise TypeError("Il consumo di mana della pozione deve essere un intero")
        if mana_consume < 0:
            raise ValueError("Il consumo di mana della pozione non può essere negativo")
        if not isinstance(uses, int):
            raise TypeError("Il numero di usi deve essere un intero")
        if uses <= 0:
            raise ValueError("Il numero di usi deve essere maggiore di 0")
        self.__name = name
        self.__mana_consume = mana_consume
        self.__uses = uses

    @property
    def name(self):
        return self.__name

    @property
    def mana_consume(self):
        return self.__mana_consume

    @property
    def uses(self):
        return self.__uses

    @abstractmethod
    def use(self, character: Character):
        pass

class HealPotion(Potion):
    def __init__(self, name: str, mana_consume: int, healing_effect: int, uses=1):
        super().__init__(name, mana_consume, uses)
        if not isinstance(healing_effect, int):
            raise TypeError("L'effetto di cura deve essere un intero")
        if healing_effect <= 0:
            raise ValueError("L'effetto di cura deve essere maggiore di 0")
        self.__healing_effect = healing_effect

    @property
    def healing_effect(self):
        return self.__healing_effect

    def use(self, character: Character):
        if not isinstance(character, Character):
            raise TypeError("Una pozione può essere utilizzata solo su un personaggio")
        character.hp = min(character.max_hp, (character.hp + self.healing_effect))

    def __str__(self):
        return f"{self.name}: pozione dal costo di {self.mana_consume} che cura {self.__healing_effect} e può essere utilizzata {self.uses} volte"

class BuffPotion(Potion):
    def __init__(self, name: str, mana_consume: int, buff: Buff, uses=1):
        super().__init__(name, mana_consume, uses)
        if not isinstance(buff, Buff):
            raise TypeError("Il buff dato dalla pozione deve essere un'istanza di Buff")
        self.__buff = buff

    @property
    def buff(self):
        return self.__buff

    def use(self, character: Character):
        if not isinstance(character, Character):
            raise TypeError("Una pozione può essere utilizzata solo su un personaggio")
        try:
            character.add_buff(self.buff)
        except AttributeError:
            raise ValueError("Personaggio non valido")

    def __str__(self):
        return f"{self.name}: pozione dal costo di {self.mana_consume} che aggiunge il buff {self.buff} \nPuò essere usata {self.uses} volte"