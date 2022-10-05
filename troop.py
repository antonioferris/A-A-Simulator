"""
    This file contains the Army class to represent A&A troops.
"""
from enum import Enum

class Power(Enum):
    R = 1
    G = 2
    UK = 3
    J = 4
    US = 5

class Troop(Enum):
    inf = 1
    art = 2
    tank = 3
    aa = 4
    trans = 5
    cruiser = 6
    carrier = 7
    battleship = 8
    fighter = 9
    bomber = 10

ATTACK_HIT_DIE = {
    Troop.inf : 1,
    Troop.art : 2,
    Troop.tank : 3,
    Troop.cruiser : 3,
    Troop.battleship : 4,
    Troop.fighter : 3,
    Troop.bomber : 4,
}

DEFENSE_HIT_DIE = {
    Troop.inf : 2,
    Troop.art : 2,
    Troop.tank : 3,
    Troop.aa : 1,
    Troop.cruiser : 3,
    Troop.battleship : 4,
    Troop.fighter : 3,
    Troop.bomber : 4,
}

LOSS_ORDER_TROOP = {
    'I' : Troop.inf,
    'A' : Troop.art,
    'T' : Troop.tank,
    'F' : Troop.fighter,
    'B' : Troop.bomber,
    'G' : Troop.aa,
}

TROOP_IPC_VALUE = {
    Troop.inf : 3,
    Troop.art : 4,
    Troop.tank : 6,
    Troop.aa : 5,
    Troop.trans : 7,
    Troop.cruiser : 12,
    Troop.carrier : 14,
    Troop.battleship : 20,
    Troop.fighter : 10,
    Troop.bomber : 12
}

AIR_UNITS = [
    Troop.fighter,
    Troop.bomber
]

class Army:
    def __init__(self, owner):
        self.owner = owner
        self.troops = {
            troop : 0 for troop in Troop
        }

    def value(self):
        return sum([cnt * TROOP_IPC_VALUE[troop] for troop, cnt in self.troops.items()])

    def __str__(self):
        s = f"{self.owner.name if self.owner else ''} Army:\n"
        for troop, cnt in self.troops.items():
            if cnt != 0:
                s += f"{cnt} {troop.name}\n"
        return s + "\n"

    def __repr__(self):
        s = "<"
        for troop, cnt in self.troops.items():
            if cnt != 0:
                s += f"({troop.name},{cnt})>"

    def __len__(self):
        return sum(self.troops.values())

    def __getitem__(self, key):
        return self.troops[key]

    def __setitem__(self, key, value):
        self.troops[key] = value

    def __add__(self, other):
        r = Army(self.owner)
        for troop in Troop:
            r.troops[troop] += self[troop] + other[troop]
        return r

def main():
    pass

if __name__ == '__main__':
    main()
