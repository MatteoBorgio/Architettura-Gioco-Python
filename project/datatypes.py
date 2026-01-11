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

@dataclass
class Buff:
    name: str
    stat: str
    amount: int
    duration: int

    def __post_init__(self):
        if not isinstance(self.name, str) or not self.name:
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
