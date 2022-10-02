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

class Army:
    def __init__(self, owner):
        self.owner = owner
        self.troops = {
            troop : 0 for troop in Troop
        }

    def __str__(self):
        s = f"{self.owner.name} Army:\n"
        for troop, cnt in self.troops.items():
            if cnt != 0:
                s += f"{cnt} {troop.name}\n"
        return s + "\n"

    def __getitem__(self, key):
        return self.troops[key]

    def __setitem__(self, key, value):
        self.troops[key] = value

    def __add__(self, other):
        if self.owner != other.owner:
            raise ValueError("Cannot add two armies owned by different powers.")
        r = Army(self.owner)
        for troop in Troop:
            r.troops[troop] += self[troop] + other[troop]
        return r

def main():
    pass

if __name__ == '__main__':
    main()
