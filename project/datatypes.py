from dataclasses import dataclass

@dataclass
class Stats:
    strength: int
    intelligence: int
    defense: int
    dexterity: int

    def __post_init__(self):
        for name, value in vars(self).items():
            if not isinstance(value, int):
                raise TypeError(f"{name} deve essere un intero")
            if value < 0:
                raise ValueError(f"{name} non può essere negativo")

    def __add__(self, other: "Stats"):
        if not isinstance(other, Stats):
            return NotImplemented

        return Stats(
            strength = self.strength + other.strength,
            intelligence = self.intelligence + other.intelligence,
            defense = self.defense + other.defense,
            dexterity = self.dexterity + other.dexterity
        )

    def __sub__(self, other: "Stats"):
        if not isinstance(other, Stats):
            return NotImplemented

        return Stats(
            strength = max(0, (self.strength - other.strength)),
            intelligence = max(0, (self.intelligence - other.intelligence)),
            defense = max(0, (self.defense - other.defense)),
            dexterity = max(0, (self.dexterity - other.dexterity))
        )

    def __str__(self):
        return f"Strength: {self.strength}; Intelligence: {self.intelligence}; Defense: {self.defense}; Dexterity: {self.dexterity}"

@dataclass
class Buff:
    name: str
    stat: str
    amount: int
    duration: int
    applied: bool=False

    def __post_init__(self):
        if not isinstance(self.name, str) or self.name == "":
            raise ValueError("Il nome deve essere una stringa non vuota")
        if self.stat not in ["defense", "strength", "dexterity", "intelligence"]:
            raise ValueError("La statistica data non è una statistica valida")
        if not isinstance(self.amount, int):
            raise TypeError("La quantità deve essere un intero")
        if self.amount < 0:
            raise ValueError("La quantità non può essere negativa")
        if not isinstance(self.duration, int):
            raise TypeError("La durata deve essere un intero")
        if self.duration <= 0:
            raise ValueError("La durata deve essere maggiore di 0")

    def __str__(self):
        return f"{self.name} che potenzia {self.stat} di {self.amount} per {self.duration} turni"

@dataclass
class Poison:
    name: str
    damage_per_turn: int
    duration: int

    def __post_init__(self):
        if not isinstance(self.name, str) or self.name == "":
            raise ValueError("Il nome deve essere una stringa non vuota")
        if not isinstance(self.damage_per_turn, int):
            raise TypeError("I danni inflitti ogni turno devono essere rappresentati da un intero")
        if self.damage_per_turn <= 0:
            raise ValueError("I danni inflitti ogni turno devono essere maggiori di 0")
        if not isinstance(self.duration, int):
            raise TypeError("La durata deve essere un intero")
        if self.duration <= 0:
            raise ValueError("La durata deve essere maggiore di 0")

    def __str__(self):
        return f"{self.name} che infligge {self.damage_per_turn} per turno per {self.duration} turni"

