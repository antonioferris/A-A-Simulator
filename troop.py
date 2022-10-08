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
    supported_inf = 11 # used for internal calculations with infantry hitting on a 2 with artillery

ATTACK_HIT_DIE = { # hit die for troops on the attack
    Troop.inf : 1,
    Troop.art : 2,
    Troop.tank : 3,
    Troop.cruiser : 3,
    Troop.battleship : 4,
    Troop.fighter : 3,
    Troop.bomber : 4,
    Troop.supported_inf : 2
}

DEFENSE_HIT_DIE = { # hit die for troops on the defense
    Troop.inf : 2,
    Troop.art : 2,
    Troop.tank : 3,
    Troop.aa : 0,
    Troop.cruiser : 3,
    Troop.battleship : 4,
    Troop.fighter : 3,
    Troop.bomber : 4,
}

LOSS_ORDER_TROOP = { # map from the character loss order to the Troop enum value
    'I' : Troop.inf,
    'A' : Troop.art,
    'T' : Troop.tank,
    'F' : Troop.fighter,
    'B' : Troop.bomber,
    'G' : Troop.aa,
    'S' : Troop.supported_inf
}

TROOP_IPC_VALUE = { # map from Troop enum to their IPC value
    Troop.inf : 3,
    Troop.art : 4,
    Troop.tank : 6,
    Troop.aa : 5,
    Troop.trans : 7,
    Troop.cruiser : 12,
    Troop.carrier : 14,
    Troop.battleship : 20,
    Troop.fighter : 10,
    Troop.bomber : 12,
    Troop.supported_inf : 3
}

AIR_UNITS = [
    Troop.fighter,
    Troop.bomber
]

NAVAL_UNITS = [
    Troop.cruiser,
    Troop.battleship
]

class Army:
    def __init__(self, owner):
        self.owner = owner
        self.troops = {
            troop : 0 for troop in Troop
        }

    def value(self):
        # return value of all units in the army
        return sum([cnt * TROOP_IPC_VALUE[troop] for troop, cnt in self.troops.items()])

    def __str__(self):
        # print the army, troops by line
        s = f"{self.owner.name if self.owner else ''} Army:\n"
        for troop, cnt in self.troops.items():
            if cnt != 0:
                s += f"{cnt} {troop.name}\n"
        return s

    def __repr__(self):
        # print the army in a more condensed form
        s = "<"
        for troop, cnt in self.troops.items():
            if cnt != 0:
                s += f"({troop.name},{cnt})>"

    def __getitem__(self, key): # internal method to let [] dict indexing work on armies
        return self.troops[key]

    def __setitem__(self, key, value):
        self.troops[key] = value

    def __add__(self, other): # allow adding of armies together.
        r = Army(self.owner)
        for troop in Troop:
            r.troops[troop] += self[troop] + other[troop]
        return r

def main():
    pass

if __name__ == '__main__':
    main()
